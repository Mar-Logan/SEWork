from django.contrib import admin

# Import all models from the current app
from .models import *

# Register the Department model with the admin site
admin.site.register(Department)
