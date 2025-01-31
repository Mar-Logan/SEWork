from django.contrib import admin
from .models import *

# Registers the Supplier model with the admin site for management.
admin.site.register(Supplier)

# Registers the PurchaseOrder model with the admin site for management.
admin.site.register(PurchaseOrder)

