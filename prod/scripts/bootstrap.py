import os
import sys
from pathlib import Path

import django


def main() -> None:
    # When executed as "python scripts/bootstrap.py", sys.path[0] becomes "/app/scripts".
    # Ensure project root is importable so "config" module can be found.
    project_root = str(Path(__file__).resolve().parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    from django.contrib.auth import get_user_model

    User = get_user_model()

    email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")

    if not email or not password:
        print("Skipping superuser creation (missing DJANGO_SUPERUSER_EMAIL or DJANGO_SUPERUSER_PASSWORD).")
        return

    if User.objects.filter(email=email).exists():
        print(f"Superuser already exists: {email}")
        return

    User.objects.create_superuser(email=email, password=password)
    print(f"Superuser created: {email}")


if __name__ == "__main__":
    main()

