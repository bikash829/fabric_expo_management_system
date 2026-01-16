from django.apps import AppConfig


class BulkCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bulk_core'
    
    def ready(self):
        # Import signals so Django registers them
        import bulk_core.signals
