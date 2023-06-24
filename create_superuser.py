import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "greatkart.settings")
django.setup()

from django.contrib.auth import get_user_model

def create_superuser(first_name,last_name,username, email, password=None):
    User = get_user_model()
    try:
        check_exist = User.objects.filter(email=email).exists()
        if not check_exist:
            User.objects.create_superuser(first_name,last_name,username, email, password)
            print("Superuser created successfully")
    except:pass



