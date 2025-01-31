from django.contrib import admin

# Import all models from the current app
from .models import *

# Register the Product, Store, and StockLocation models to be accessible through the Django admin interface.
admin.site.register(Product)
admin.site.register(Store)
admin.site.register(ProductLocation)
