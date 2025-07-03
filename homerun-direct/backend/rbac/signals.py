def create_super_user(sender, **kwargs):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    username = "nishu"
    email = "nishant@directsoftware.com"
    password = "nishu"

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✅ Superuser '{username}' created.")
    else:
        print(f"ℹ️ Superuser '{username}' already exists.")
    
def initiate_rbac(sender, **kwargs):
    create_super_user(sender, **kwargs)
    

