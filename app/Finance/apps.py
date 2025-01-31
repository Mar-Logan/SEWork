from django.apps import AppConfig

# Configuration class for the "Finance" app
class FinanceConfig(AppConfig):
    # Specifies the default auto field type for model primary keys
    default_auto_field = "django.db.models.BigAutoField"
    # App name
    name = "Finance"

