from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            return render(request, "accounts/signup.html", {
                "error": "Passwords do not match"
            })

        if User.objects.filter(username=username).exists():
            return render(request, "accounts/signup.html", {
                "error": "Username already exists"
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)
        return redirect("inventory_list")

    return render(request, "accounts/signup.html")

def add_account(request):
    if request.method == "POST":
        # process form
        pass
    return render(request, "accounts/add_account.html")



def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # Redirect superuser to dashboard, normal users to inventory
            if user.is_superuser:
                return redirect('/dashboard/')  # ← THIS FIXES /home/ 404
            else:
                return redirect('/inventory/')
        else:
            error = "Invalid username or password"
    return render(request, "accounts/login.html", {"error": error})
