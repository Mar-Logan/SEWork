from django.apps import AppConfig

# Configuration class for the 'Inventory' app.
# Specifies the default auto field type for models and the name of the app.
class InventoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # Default primary key type for models
    name = "Inventory"  # Name of the app
