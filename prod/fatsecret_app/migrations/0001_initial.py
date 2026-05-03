import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="FatSecretOAuth",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("access_token", models.TextField()),
                ("access_token_secret", models.TextField()),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fatsecret_oauth",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "fatsecret_oauth"},
        ),
        migrations.CreateModel(
            name="FatSecretSyncState",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("last_sync_at", models.DateTimeField(blank=True, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fatsecret_sync",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "fatsecret_sync_state"},
        ),
        migrations.CreateModel(
            name="FSProfileData",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("goal_weight_kg", models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ("height_cm", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("height_measure", models.CharField(blank=True, max_length=32)),
                ("last_weight_date_int", models.BigIntegerField(blank=True, null=True)),
                ("last_weight_kg", models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ("weight_measure", models.CharField(blank=True, max_length=32)),
                ("fetched_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fs_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "fs_profile_data"},
        ),
        migrations.CreateModel(
            name="FSFoodDiary",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("diary_date", models.DateField(db_index=True)),
                ("date_int", models.IntegerField()),
                ("food_entry_id", models.BigIntegerField()),
                ("food_entry_name", models.TextField(blank=True)),
                ("food_entry_description", models.TextField(blank=True)),
                ("food_id", models.BigIntegerField(blank=True, null=True)),
                ("meal", models.CharField(blank=True, max_length=64)),
                ("serving_id", models.BigIntegerField(blank=True, null=True)),
                ("number_of_units", models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True)),
                ("calories", models.IntegerField(blank=True, null=True)),
                ("carbohydrate", models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True)),
                ("fat", models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True)),
                ("protein", models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True)),
                ("fiber", models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True)),
                ("sugar", models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True)),
                ("sodium", models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True)),
                ("cholesterol", models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True)),
                ("saturated_fat", models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True)),
                ("monounsaturated_fat", models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True)),
                ("polyunsaturated_fat", models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True)),
                ("potassium", models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True)),
                ("calcium", models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True)),
                ("iron", models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True)),
                ("vitamin_a", models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True)),
                ("vitamin_c", models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fs_food_entries",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "fs_food_diary",
                "indexes": [models.Index(fields=["user", "diary_date"], name="fs_food_diary_user_id_diary_date_idx")],
            },
        ),
        migrations.AddConstraint(
            model_name="fsfooddiary",
            constraint=models.UniqueConstraint(fields=("user", "food_entry_id"), name="fs_food_diary_user_food_entry_id_uniq"),
        ),
    ]
