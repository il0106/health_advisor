from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm
from .models import User


def register_view(request):
    if request.user.is_authenticated:
        return redirect("me")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password1"]

        if User.objects.filter(email=email).exists():
            form.add_error("email", "Пользователь с таким email уже существует")
        else:
            User.objects.create_user(email=email, password=password)
            messages.success(request, "Аккаунт создан. Теперь войдите.")
            return redirect("login")

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("me")

    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]

        user = authenticate(request, username=email, password=password)
        if user is None:
            form.add_error(None, "Неверный email или пароль")
        else:
            login(request, user)
            return redirect("me")

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("landing")

