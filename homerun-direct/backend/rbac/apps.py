from django.apps import AppConfig


class RbacConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rbac'

    def ready(self):
        """
        * No extra migration file needed   
        * Auto-inserts only after all migrations are done
        * Works even after you delete migration files
        * Does not duplicate values if already present
        """
        from django.db.models.signals import post_migrate
        from .signals import initiate_rbac
        post_migrate.connect(initiate_rbac, sender=self)
