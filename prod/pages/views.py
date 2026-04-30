from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def landing(request):
    return render(request, "pages/landing.html")


@login_required
def me(request):
    return render(request, "pages/me.html")

