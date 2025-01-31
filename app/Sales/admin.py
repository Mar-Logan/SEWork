from django.contrib import admin

from .models import *

# Registers the Sales model with Django admin site to allow management through the admin interface
admin.site.register(Sales)
