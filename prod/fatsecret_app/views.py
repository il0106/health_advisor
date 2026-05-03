from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .models import FSFoodDiary, FSProfileData, FatSecretOAuth, FatSecretSyncState
from . import services


@login_required
def monitor(request):
    if request.method == "POST" and request.POST.get("action") == "sync":
        try:
            services.sync_fatsecret_for_user(request.user)
            messages.success(request, "Данные FatSecret обновлены.")
        except Exception as e:
            messages.error(request, str(e))
        return redirect("monitor")

    profile = None
    try:
        profile = request.user.fs_profile
    except FSProfileData.DoesNotExist:
        pass

    sync_state = None
    try:
        sync_state = request.user.fatsecret_sync
    except FatSecretSyncState.DoesNotExist:
        pass

    diary_sample = list(
        FSFoodDiary.objects.filter(user=request.user).order_by("-diary_date", "-id")[:5]
    )

    has_oauth = FatSecretOAuth.objects.filter(user=request.user).exists()

    return render(
        request,
        "fatsecret/monitor.html",
        {
            "fs_profile": profile,
            "last_sync_at": sync_state.last_sync_at if sync_state else None,
            "diary_sample": diary_sample,
            "has_oauth": has_oauth,
        },
    )


@login_required
def fs_connect(request):
    """Поток аутентификации из ноутбука: request_token → ссылка → PIN → access_token в БД."""
    auth_url = request.session.get("fs_auth_url")
    if request.method == "POST":
        step = request.POST.get("step", "")
        if step == "1":
            try:
                rt, rts, auth_url = services.oauth_request_token()
            except Exception as e:
                messages.error(request, str(e))
            else:
                request.session["fs_rt"] = rt
                request.session["fs_rts"] = rts
                request.session["fs_auth_url"] = auth_url
                messages.info(
                    request,
                    "Откройте ссылку, подтвердите доступ в FatSecret и введите PIN ниже.",
                )
                return redirect("fs_connect")
        elif step == "2":
            pin = (request.POST.get("pin") or "").strip()
            rt = request.session.get("fs_rt")
            rts = request.session.get("fs_rts")
            if not pin or not rt or not rts:
                messages.error(request, "Сначала получите ссылку (шаг 1) и введите PIN.")
            else:
                try:
                    at, ats = services.oauth_access_token(rt, rts, pin)
                except Exception as e:
                    messages.error(request, str(e))
                else:
                    services.save_oauth_tokens(request.user, at, ats)
                    request.session.pop("fs_rt", None)
                    request.session.pop("fs_rts", None)
                    request.session.pop("fs_auth_url", None)
                    messages.success(request, "FatSecret подключён. Можно нажать «Обновить данные» на мониторе.")
                    return redirect("monitor")

    return render(request, "fatsecret/connect.html", {"auth_url": auth_url})
