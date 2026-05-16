from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Jewelry, Comment, Like, Banner
from .forms import JewelryForm, BannerForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.contrib import messages
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

# --- Helper functions ---
def is_admin(user):
    return user.is_staff or user.is_superuser

def staff_check(user):
    return user.is_staff

# --- Home page ---
def home(request):
    query = request.GET.get('q', '')
    if query:
        items = Jewelry.objects.filter(
            Q(name__icontains=query) | Q(category__icontains=query)
        )
    else:
        items = Jewelry.objects.all()

    banners = Banner.objects.all()
    top_banner = banners.filter(banner_type='top').first()
    bottom_banners = banners.filter(banner_type__startswith='bottom')

    context = {
        'items': items,
        'top_banner': top_banner,
        'bottom_banners': bottom_banners,
    }
    return render(request, 'inventory/home.html', context)

# --- Stripe Checkout ---
def create_checkout(request, item_id):
    item = get_object_or_404(Jewelry, id=item_id)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.name,
                    'description': item.description or '',
                },
                'unit_amount': int(item.price * 100),  # Stripe uses cents
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri('/payment/success/'),
        cancel_url=request.build_absolute_uri(f'/inventory/{item_id}/'),
    )

    return redirect(session.url)

# --- Payment Success ---
def payment_success(request):
    return render(request, 'inventory/payment_success.html')

# --- Collections page ---
def collections(request):
    query = request.GET.get('q', '')
    if query:
        items = Jewelry.objects.filter(
            Q(name__icontains=query) | Q(category__icontains=query)
        )
    else:
        items = Jewelry.objects.all()
    return render(request, 'inventory/collection.html', {'items': items})

# --- Single Collection page ---
def collection(request, item_id):
    item = get_object_or_404(Jewelry, id=item_id)
    return render(request, 'inventory/collection.html', {'item': item})

# --- Details page ---
def details(request, item_id):
    item = get_object_or_404(Jewelry, id=item_id)
    other_items = Jewelry.objects.exclude(id=item_id)[:4]

    if request.method == 'POST':
        if 'comment' in request.POST:
            Comment.objects.create(
                item=item,
                user=request.user,
                text=request.POST['comment']
            )
        elif 'like' in request.POST:
            like, created = Like.objects.get_or_create(item=item, user=request.user)
            if not created:
                like.delete()
        return redirect('inventory_details', item_id=item.id)

    return render(request, 'inventory/details.html', {'item': item, 'other_items': other_items})

# --- Inventory list (admin) ---
@login_required
@user_passes_test(staff_check)
def inventory_list(request):
    query = request.GET.get('q', '')
    if query:
        items = Jewelry.objects.filter(
            Q(name__icontains=query) | Q(category__icontains=query)
        )
    else:
        items = Jewelry.objects.all()
    banners = Banner.objects.all()
    return render(request, 'inventory/inventory_list.html', {'items': items, 'banners': banners})

# --- Banner list (admin) ---
@login_required
@user_passes_test(staff_check)
def banner_list(request):
    banners = Banner.objects.all().order_by('-created_at')
    return render(request, 'inventory/banner_list.html', {'banners': banners})

# --- Add new banner ---
@login_required
@user_passes_test(staff_check)
def banner_add(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('banner_list')
    else:
        form = BannerForm()
    return render(request, 'inventory/banner_form.html', {'form': form, 'action': 'Add'})

# --- Edit banner ---
@login_required
@user_passes_test(staff_check)
def banner_edit(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            return redirect('banner_list')
    else:
        form = BannerForm(instance=banner)
    return render(request, 'dashboard/banner_form.html', {'form': form, 'action': 'Edit'})

# --- Delete banner ---
@login_required
@user_passes_test(staff_check)
def banner_delete(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        banner.delete()
        return redirect('banner_list')
    return render(request, 'inventory/banner_delete_confirm.html', {'banner': banner})

# --- User signup ---
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST.get('confirm_password') or request.POST.get('password2')

        if password != confirm_password:
            return render(request, 'accounts/signup.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/signup.html', {'error': 'Username already exists'})

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('inventory_list')

    return render(request, 'accounts/signup.html')

# --- User login ---
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_staff or user.is_superuser:
                return redirect('/admin/')
            else:
                return redirect('inventory_list')
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid username or password'})

    return render(request, 'accounts/login.html')

# --- User logout ---
def logout_view(request):
    logout(request)
    return redirect('login')

# --- Add new item (admin only) ---
@login_required
@user_passes_test(staff_check)
def add_item(request):
    if request.method == 'POST':
        form = JewelryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        form = JewelryForm()
    return render(request, 'inventory/add_item.html', {'form': form})

# --- Account creation ---
@login_required
def account_create(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            User.objects.create_user(username=username, password=password)
            messages.success(request, "Account created successfully!")
            return redirect('login')
        else:
            messages.error(request, "Please fill out all fields.")
    return render(request, 'inventory/account_add.html')


from django.shortcuts import render

def cart(request):
    return render(request, 'cart.html')

def wishlist(request):
    return render(request, 'wishlist.html')