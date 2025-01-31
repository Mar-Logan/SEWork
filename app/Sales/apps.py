from django.apps import AppConfig


class SalesConfig(AppConfig):       # Configures the Sales app for Django, specifying default auto field type
    default_auto_field = "django.db.models.BigAutoField"
    name = "Sales"  # app name
