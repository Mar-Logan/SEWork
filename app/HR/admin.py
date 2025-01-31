from django.contrib import admin

# Import all models from the current app
from .models import *

# Register the Staff model with the admin site
admin.site.register(Staff)
