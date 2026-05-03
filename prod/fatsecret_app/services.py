from __future__ import annotations

import os
import time
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import parse_qs

from requests_oauthlib import OAuth1Session

from django.db import transaction
from django.utils import timezone

from .models import FSFoodDiary, FSProfileData, FatSecretOAuth, FatSecretSyncState


def _consumer_credentials() -> tuple[str, str]:
    key = os.environ.get("FATSECRET_CONSUMER_KEY") or os.environ.get("ConsumerKey", "")
    secret = os.environ.get("FATSECRET_CONSUMER_SECRET") or os.environ.get("ConsumerSecret", "")
    if not key or not secret:
        raise RuntimeError(
            "Не заданы FATSECRET_CONSUMER_KEY и FATSECRET_CONSUMER_SECRET в окружении."
        )
    return key, secret


def parse_token(text: str) -> tuple[str | None, str | None]:
    data = parse_qs(text)
    return (data.get("oauth_token", [None])[0], data.get("oauth_token_secret", [None])[0])


def oauth_request_token() -> tuple[str, str, str]:
    """Шаг 1 ноутбука: request_token + URL авторизации."""
    client_id, client_secret = _consumer_credentials()
    session = OAuth1Session(client_id, client_secret, callback_uri="oob", signature_type="BODY")
    resp = session.post("https://authentication.fatsecret.com/oauth/request_token")
    resp.raise_for_status()
    request_token, request_token_secret = parse_token(resp.text)
    if not request_token or not request_token_secret:
        raise RuntimeError(f"Не удалось разобрать request_token: {resp.text}")
    auth_url = f"https://authentication.fatsecret.com/oauth/authorize?oauth_token={request_token}"
    return request_token, request_token_secret, auth_url


def oauth_access_token(
    request_token: str,
    request_token_secret: str,
    verifier: str,
) -> tuple[str, str]:
    """Шаг 2 ноутбука: обмен PIN на access_token."""
    client_id, client_secret = _consumer_credentials()
    access_session = OAuth1Session(
        client_id,
        client_secret,
        resource_owner_key=request_token,
        resource_owner_secret=request_token_secret,
        verifier=verifier.strip(),
        signature_type="BODY",
    )
    resp = access_session.post("https://authentication.fatsecret.com/oauth/access_token")
    resp.raise_for_status()
    access_token, access_token_secret = parse_token(resp.text)
    if not access_token or not access_token_secret:
        raise RuntimeError(f"Не удалось разобрать access_token: {resp.text}")
    return access_token, access_token_secret


def build_api_session(user) -> OAuth1Session | None:
    """Сессия как api_session в ноутбуке (после получения access_token)."""
    try:
        row = FatSecretOAuth.objects.get(user=user)
    except FatSecretOAuth.DoesNotExist:
        return None
    client_id, client_secret = _consumer_credentials()
    return OAuth1Session(
        client_id,
        client_secret,
        resource_owner_key=row.access_token,
        resource_owner_secret=row.access_token_secret,
    )


def date_to_int(d: date) -> int:
    return (d - date(1970, 1, 1)).days


def int_to_date(n: int) -> date:
    return date(1970, 1, 1) + timedelta(days=int(n))


def _to_decimal(val: Any) -> Decimal | None:
    if val is None or val == "":
        return None
    if isinstance(val, (int, float, Decimal)):
        return Decimal(str(val))
    s = str(val).replace("\xa0", "").replace(" ", "").strip()
    if not s:
        return None
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def _to_int(val: Any) -> int | None:
    if val is None or val == "":
        return None
    try:
        return int(Decimal(str(val).replace("\xa0", "").replace(" ", "")))
    except (InvalidOperation, ValueError):
        try:
            return int(val)
        except (TypeError, ValueError):
            return None


def normalize_food_entries(payload: dict) -> list[dict]:
    fe = payload.get("food_entries") or {}
    raw = fe.get("food_entry")
    if raw is None:
        return []
    if isinstance(raw, dict):
        return [raw]
    return list(raw)


def fetch_profile(session: OAuth1Session) -> dict:
    response = session.get(
        "https://platform.fatsecret.com/rest/server.api",
        params={"method": "profile.get", "format": "json"},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def fetch_food_entries_for_date(session: OAuth1Session, d: date) -> dict:
    response = session.get(
        "https://platform.fatsecret.com/rest/server.api",
        params={
            "method": "food_entries.get.v2",
            "format": "json",
            "date": date_to_int(d),
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


@transaction.atomic
def save_profile(user, data: dict) -> FSProfileData:
    profile = (data or {}).get("profile") or {}
    obj, _ = FSProfileData.objects.update_or_create(
        user=user,
        defaults={
            "goal_weight_kg": _to_decimal(profile.get("goal_weight_kg")),
            "height_cm": _to_decimal(profile.get("height_cm")),
            "height_measure": (profile.get("height_measure") or "")[:32],
            "last_weight_date_int": _to_int(profile.get("last_weight_date_int")),
            "last_weight_kg": _to_decimal(profile.get("last_weight_kg")),
            "weight_measure": (profile.get("weight_measure") or "")[:32],
        },
    )
    return obj


def upsert_food_row(user, row: dict, diary_date: date, date_int: int) -> None:
    fe_id = _to_int(row.get("food_entry_id"))
    if fe_id is None:
        return
    defaults = {
        "diary_date": diary_date,
        "date_int": date_int,
        "food_entry_name": row.get("food_entry_name") or "",
        "food_entry_description": row.get("food_entry_description") or "",
        "food_id": _to_int(row.get("food_id")),
        "meal": (row.get("meal") or "")[:64],
        "serving_id": _to_int(row.get("serving_id")),
        "number_of_units": _to_decimal(row.get("number_of_units")),
        "calories": _to_int(row.get("calories")),
        "carbohydrate": _to_decimal(row.get("carbohydrate")),
        "fat": _to_decimal(row.get("fat")),
        "protein": _to_decimal(row.get("protein")),
        "fiber": _to_decimal(row.get("fiber")),
        "sugar": _to_decimal(row.get("sugar")),
        "sodium": _to_decimal(row.get("sodium")),
        "cholesterol": _to_decimal(row.get("cholesterol")),
        "saturated_fat": _to_decimal(row.get("saturated_fat")),
        "monounsaturated_fat": _to_decimal(row.get("monounsaturated_fat")),
        "polyunsaturated_fat": _to_decimal(row.get("polyunsaturated_fat")),
        "potassium": _to_decimal(row.get("potassium")),
        "calcium": _to_decimal(row.get("calcium")),
        "iron": _to_decimal(row.get("iron")),
        "vitamin_a": _to_decimal(row.get("vitamin_a")),
        "vitamin_c": _to_decimal(row.get("vitamin_c")),
    }
    FSFoodDiary.objects.update_or_create(
        user=user,
        food_entry_id=fe_id,
        defaults=defaults,
    )


def _food_diary_history_offset_days() -> int:
    """Сколько дней назад от даты синхронизации начинать период (см. .env FATSECRET_FOOD_DIARY_DAYS)."""
    raw = os.environ.get("FATSECRET_FOOD_DIARY_DAYS", "365").strip()
    try:
        n = int(raw)
    except ValueError:
        n = 365
    return max(0, min(n, 4000))


def sync_fatsecret_for_user(user, end_date: date | None = None) -> None:
    """
    Полный цикл: профиль + дневник за период до end_date (включительно).
    Глубина истории задаётся FATSECRET_FOOD_DIARY_DAYS: период [end - N дней, end].
    Дни, для которых в fs_food_diary уже есть строки, пропускаются (без запроса API).
    """
    session = build_api_session(user)
    if session is None:
        raise RuntimeError("FatSecret не подключён: сохраните OAuth токены (PIN).")

    end = end_date or timezone.localdate()
    n = _food_diary_history_offset_days()
    start = end - timedelta(days=n)

    prof = fetch_profile(session)
    save_profile(user, prof)

    d = start
    while d <= end:
        has_rows = FSFoodDiary.objects.filter(user=user, diary_date=d).exists()
        if not has_rows:
            payload = fetch_food_entries_for_date(session, d)
            di = date_to_int(d)
            for row in normalize_food_entries(payload):
                upsert_food_row(user, row, d, di)
            time.sleep(1)

        d += timedelta(days=1)

    FatSecretSyncState.objects.update_or_create(
        user=user,
        defaults={"last_sync_at": timezone.now()},
    )


def save_oauth_tokens(user, access_token: str, access_token_secret: str) -> None:
    FatSecretOAuth.objects.update_or_create(
        user=user,
        defaults={
            "access_token": access_token,
            "access_token_secret": access_token_secret,
        },
    )
