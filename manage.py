#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import dotenv

dotenv.load_dotenv()

from create_superuser import create_superuser

start_user = create_superuser(os.environ.get("SU_FIRST_NAME"),
                              os.environ.get("SU_LAST_NAME"),
                              os.environ.get("SU_USERNAME"),
                              os.environ.get("SU_EMAIL"),
                              os.environ.get("SU_PASSWORD"), )


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatkart.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
    start_user
