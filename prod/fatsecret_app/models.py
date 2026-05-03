from django.conf import settings
from django.db import models


class FatSecretOAuth(models.Model):
    """OAuth-токены пользователя FatSecret (после PIN-как в ноутбуке)."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="fatsecret_oauth")
    access_token = models.TextField()
    access_token_secret = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fatsecret_oauth"


class FatSecretSyncState(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="fatsecret_sync")
    last_sync_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "fatsecret_sync_state"


class FSProfileData(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="fs_profile")
    goal_weight_kg = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height_measure = models.CharField(max_length=32, blank=True)
    last_weight_date_int = models.BigIntegerField(null=True, blank=True)
    last_weight_kg = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    weight_measure = models.CharField(max_length=32, blank=True)
    fetched_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fs_profile_data"


class FSFoodDiary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="fs_food_entries")
    diary_date = models.DateField(db_index=True)
    date_int = models.IntegerField()
    food_entry_id = models.BigIntegerField()
    food_entry_name = models.TextField(blank=True)
    food_entry_description = models.TextField(blank=True)
    food_id = models.BigIntegerField(null=True, blank=True)
    meal = models.CharField(max_length=64, blank=True)
    serving_id = models.BigIntegerField(null=True, blank=True)
    number_of_units = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    calories = models.IntegerField(null=True, blank=True)
    carbohydrate = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    fat = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    protein = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    fiber = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    sugar = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    sodium = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    cholesterol = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    saturated_fat = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    monounsaturated_fat = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    polyunsaturated_fat = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    potassium = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    calcium = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    iron = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    vitamin_a = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    vitamin_c = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fs_food_diary"
        constraints = [
            models.UniqueConstraint(fields=["user", "food_entry_id"], name="fs_food_diary_user_food_entry_id_uniq")
        ]
        indexes = [
            models.Index(fields=["user", "diary_date"]),
        ]
