from django.apps import AppConfig

class MasterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'master'

    def ready(self):
        """
        * No extra migration file needed   
        * Auto-inserts only after all migrations are done
        * Works even after you delete migration files
        * Does not duplicate values if already present
        """
        from django.db.models.signals import post_migrate
        from .signals import insert_master_data
        post_migrate.connect(insert_master_data, sender=self)
