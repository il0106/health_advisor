from django.contrib import admin

from .models import FSFoodDiary, FSProfileData, FatSecretOAuth, FatSecretSyncState


@admin.register(FatSecretOAuth)
class FatSecretOAuthAdmin(admin.ModelAdmin):
    list_display = ("user", "updated_at")
    search_fields = ("user__email",)


@admin.register(FatSecretSyncState)
class FatSecretSyncStateAdmin(admin.ModelAdmin):
    list_display = ("user", "last_sync_at")
    search_fields = ("user__email",)


@admin.register(FSProfileData)
class FSProfileDataAdmin(admin.ModelAdmin):
    list_display = ("user", "height_cm", "last_weight_kg", "fetched_at")
    search_fields = ("user__email",)


@admin.register(FSFoodDiary)
class FSFoodDiaryAdmin(admin.ModelAdmin):
    list_display = ("user", "diary_date", "food_entry_name", "calories", "meal")
    list_filter = ("diary_date", "meal")
    search_fields = ("user__email", "food_entry_name")
