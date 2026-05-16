from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, F
from django.http import HttpResponse
import requests
import openpyxl

from inventory.models import Jewelry, Banner
from .forms import JewelryForm, BannerForm


# ----------------------
# Admin check
# ----------------------
def staff_check(user):
    return user.is_staff or user.is_superuser


# ----------------------
# Dashboard home
# ----------------------
@login_required(login_url='/accounts/login/')
@user_passes_test(staff_check, login_url='/accounts/login/')
def dashboard_home(request):
    return redirect('inventory_dashboard')


# ----------------------
# Inventory Dashboard
# ----------------------
@login_required(login_url='/accounts/login/')
@user_passes_test(staff_check, login_url='/accounts/login/')
def inventory_dashboard(request):
    items = Jewelry.objects.all()
    banners = Banner.objects.all()

    # ✅ FIX: read edit_id from GET (page load) OR POST (form submit)
    edit_id = request.GET.get('edit') or request.POST.get('edit_id')
    item = get_object_or_404(Jewelry, id=edit_id) if edit_id else None

    form = JewelryForm(instance=item)
    banner_form = BannerForm()

    if request.method == 'POST':

        # ---------------- BANNER ----------------
        if request.POST.get('form_type') == 'banner':
            banner_form = BannerForm(request.POST, request.FILES)
            if banner_form.is_valid():
                banner_form.save()
                return redirect('inventory_dashboard')

        # ---------------- JEWELRY ----------------
        elif request.POST.get('form_type') == 'jewelry':
            form = JewelryForm(request.POST, request.FILES, instance=item)
            if form.is_valid():
                form.save()
                return redirect('inventory_dashboard')

    return render(request, 'dashboard/inventory.html', {
        'form': form,
        'banner_form': banner_form,
        'items': items,
        'item': item,
        'banners': banners,
    })
# ----------------------
# DELETE jewelry
# ----------------------
@login_required
@user_passes_test(staff_check)
def delete_item(request, item_id):
    if request.method == "POST":
        get_object_or_404(Jewelry, id=item_id).delete()
    return redirect('inventory_dashboard')


# ----------------------
# Banner Add/Edit/Delete
# ----------------------
@login_required
@user_passes_test(staff_check)
def add_banner(request):
    form = BannerForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('inventory_dashboard')

    return render(request, 'dashboard/banner_form.html', {
        'form': form,
        'action': 'Add'
    })


@login_required
@user_passes_test(staff_check)
def edit_banner(request, banner_id):
    banner = get_object_or_404(Banner, id=banner_id)

    form = BannerForm(request.POST or None, request.FILES or None, instance=banner)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('inventory_dashboard')

    return render(request, 'dashboard/banner_form.html', {
        'form': form,
        'action': 'Edit'
    })


@login_required
@user_passes_test(staff_check)
def delete_banner(request, banner_id):
    get_object_or_404(Banner, id=banner_id).delete()
    return redirect('inventory_dashboard')


# ----------------------
# ANALYSIS
# ----------------------
def analysis(request):

    items = Jewelry.objects.all()

    total_products = items.count()

    total_revenue = items.aggregate(
        total=Sum(F('price') * F('quantity'))
    )['total'] or 0

    total_sold = 0

    return render(request, 'dashboard/analysis.html', {
        'total_products': total_products,
        'total_revenue': total_revenue,
        'total_sold': total_sold,
    })


# ----------------------
# NEWS
# ----------------------
def news(request):

    articles = []
    crypto_price = "N/A"

    try:
        res = requests.get(
            "https://newsapi.org/v2/everything?q=gold OR silver OR crypto OR bitcoin&sortBy=publishedAt&language=en&apiKey=e44ae63bef104e81ba529c0dce1552b0",
            timeout=5
        )
        articles = res.json().get("articles", [])[:10]

    except Exception as e:
        print("News error:", e)

    try:
        res2 = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd",
            timeout=5
        )
        crypto_price = res2.json()

    except Exception as e:
        print("Crypto error:", e)

    return render(request, "dashboard/news.html", {
        "articles": articles,
        "crypto_price": crypto_price,
    })


# ----------------------
# EXPORT EXCEL
# ----------------------
def export_report_excel(request):

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Inventory Report"

    ws.append(["Product Name", "Total Stock", "Sold", "Remaining", "Sold %"])

    products = Jewelry.objects.all()

    for p in products:
        sold = getattr(p, "sold", 0)
        stock = getattr(p, "quantity", 0)

        remaining = stock - sold
        sold_percent = (sold / stock * 100) if stock else 0

        ws.append([
            p.name,
            stock,
            sold,
            remaining,
            f"{sold_percent:.2f}%"
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=report.xlsx"

    wb.save(response)
    return response


# ----------------------
# REPORT PAGE
# ----------------------
from django.utils import timezone
from datetime import timedelta

def report_page(request):
    period = request.GET.get('period', 'all')
    now = timezone.now()

    items = Jewelry.objects.all()

    if period == 'day':
        items = items.filter(created_at__date=now.date())
    elif period == 'week':
        items = items.filter(created_at__gte=now - timedelta(days=7))
    elif period == 'month':
        items = items.filter(created_at__year=now.year, created_at__month=now.month)
    elif period == 'year':
        items = items.filter(created_at__year=now.year)

    total_products = items.count()
    total_stock = items.aggregate(total=Sum('quantity'))['total'] or 0
    total_sold = sum(getattr(i, "sold", 0) for i in items)

    return render(request, "dashboard/report.html", {
        "products": items,
        "total_products": total_products,
        "total_stock": total_stock,
        "total_sold": total_sold,
        "period": period,
    })