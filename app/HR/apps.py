from django.apps import AppConfig

# Configuration class for the "HR" app
# Specifies the default auto field type for model primary keys and the app name
class HrConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # Default primary key type for models
    name = "HR"  # Name of the app
