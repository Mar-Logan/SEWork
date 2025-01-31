from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum, Avg
from datetime import datetime, timedelta


class Product(models.Model):
    # Represents a product in the inventory system with ProductType, price, stock level, and supplier.

    ProductId = models.AutoField(primary_key=True, unique=True)     # Unique identifier for the product
    ProductName = models.CharField(max_length=200)                  # Name of the product
    ProductType = models.CharField(max_length=100)                     # ProductType the product belongs to

    Price = models.DecimalField(max_digits=10, decimal_places=2)    # Price of the product
    StockAmount = models.IntegerField()                              # Quantity of the product available in stock
    OrderLimit = models.IntegerField()                            # The stock level at which the product should be reordered
    LastPurchaseDate = models.DateField(null=True, blank=True)      # Date of the last purchase of the product
    
    SupplierId = models.ForeignKey(
        "Procurement.Supplier",  # The supplier of the product
        null=True,
        related_name="products",  # Related name for accessing the products for a supplier
        on_delete=models.SET_NULL,  # If the supplier is deleted, set this field to null
    )

    # Returns a string representation of the product with its stock and reorder levels
    def __str__(self):
        return (
            f"{self.ProductName} - Level:{self.StockAmount} Order at:{self.OrderLimit}"
        )

    def GetAllStores(self): # Returns all stores that stock this product.
        return self.ProductLocation_set.values("StoreId__StoreName", "StoreId__Location")

    def GetStockAmount(self): #  Returns the total stock level for this product across all stores
        return (
            self.ProductLocation_set.aggregate(TotalStock=Sum("Quantity"))["TotalStock"]
            or 0
        )

    # Transfers stock of this product between stores
    def TransferStock(self, from_store, to_store, quantity):

        if quantity <= 0: # quantity, Quantity of stock to transfer.
            raise ValueError("Quantity must be greater than zero.")

        from_stock = self.ProductLocation.filter(StoreId=from_store).first() # from_store, Store instance to transfer from
        to_stock = self.ProductLocation.filter(StoreId=to_store).first() #  to_store, Store instance to transfer to

        if not from_stock or from_stock.Quantity < quantity:# Check if there is enough stock in the source store to transfer the requested quantity
            raise ValidationError("Insufficient stock in the source store.")


        # Reduce the quantity in the source store
        from_stock.Quantity -= quantity
        from_stock.save()

        if to_stock: # Update the stock
            to_stock.Quantity += quantity

        else:# If the product doesn't exist in the destination store, create a new stock entry
            ProductLocation.objects.create(
                ProductId=self, StoreId=to_store, Quantity=quantity
            )
        to_stock.save()# Save the updated stock

    def EditOrderLimit(self, new_reorder_level):
       # Updates the reorder level for this product, new_reorder_level: New reorder level (integer)
        if new_reorder_level < 0:
            raise ValueError("Reorder level must be a non-negative integer.")
        self.OrderLimit = new_reorder_level
        self.save()


class Store(models.Model):
    StoreId = models.AutoField(primary_key=True, unique=True)   # Unique identifier for the store
    StoreName = models.CharField(max_length=200)                # Name of the store
    Location = models.CharField(max_length=200)                 # Location of the store (e.g., address)
    ContactNumber = models.CharField(max_length=15)             # Contact number for the store
    ManagerId = models.OneToOneField(
        "HR.Staff",                                             # The store manager, a relation to the Staff model in the HR app
        null=True,                                              # Allow null if there is no manager assigned
        on_delete=models.SET_NULL,                              # If the manager is deleted, set this field to null
    )

    TotalSales = models.IntegerField()                          # The total sales amount
    OperatingHours = models.IntegerField()                      # The number of hours the store operates per day

    def __str__(self): # Returns a string representation of the store with its name and location
        return f"{self.StoreName} - {self.Location}"

    def GetAllProducts(self): # Returns all products stocked in this store.
        return self.ProductLocation_set.values("ProductId__ProductName", "Quantity")

    def ViewStorePerformance(self):
        # Returns the store's performance metrics
        return {
            "TotalSales": self.TotalSales, # total sales and average sales per hour
            "AverageSalesPerHour": (
                self.TotalSales / self.OperatingHours if self.OperatingHours else 0
            ),
        }

    def edit_store_data(self, **kwargs):
        """
        Updates store information with provided data

        Args:
            **kwargs: Dictionary of fields to update and their new values

        Returns:
            bool: True if update successful, raises exception otherwise
        """
        try:
            valid_fields = {
                "StoreName",
                "Location",
                "ContactNumber",
                "ManagerId",
                "OperatingHours",
            }
            
            update_data = {k: v for k, v in kwargs.items() if k in valid_fields}    # Filter out invalid fields
            if not update_data:
                raise ValidationError("No valid fields provided for update")

            
            if "ContactNumber" in update_data:                                      # Validate contact number format if it's being updated
                if not update_data["ContactNumber"].replace("+", "").isdigit():
                    raise ValidationError("Invalid contact number format")

           
            if "OperatingHours" in update_data:                                      # Validate operating hours if being updated
                if not 0 < update_data["OperatingHours"] <= 24:
                    raise ValidationError("Operating hours must be between 1 and 24")

            
            for field, value in update_data.items():                                 # Update the fields
                setattr(self, field, value)
            self.full_clean()                       # Validate all fields
            self.save()
            return True

        except ValidationError as ve:
            raise ValidationError(f"Validation error: {str(ve)}")   #Error with validation
        

        except Exception as e:
            raise ValueError(f"Error updating store data: {str(e)}")    #Error with store data


class ProductLocation(models.Model):
    ProductLocationId = models.AutoField(primary_key=True, unique=True)       # Unique identifier for each stock location record
    ProductId = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="ProductLocation"     # ForeignKey linking to the Product model. 
    )                                                                       #If the product is deleted, associated stock locations are also deleted

    StoreId = models.ForeignKey(                                         #  ForeignKey linking to the Store model
        Store, on_delete=models.CASCADE, related_name="ProductLocation"    # If the store is deleted, associated stock locations are also deleted.
    )
    
    Quantity = models.IntegerField()                        # The timestamp when the stock location record is created.                   
    Date = models.DateTimeField(auto_now_add=True)                  

    def __str__(self):# Returns a string representation of the stock location, showing the product name, store name, and quantity
        return f"{self.ProductId.ProductName} - {self.StoreId.StoreName} - Amount: {self.Quantity}"

    def AdjustStock(self, quantity):
        """
        Adjusts the stock quantity for this stock location.
        
        Args:
            quantity (int): Positive value to increase stock, negative to decrease stock.
        
        Raises:
            ValidationError: If the adjustment results in a negative stock quantity.
        """

        if self.Quantity + quantity < 0:
            raise ValidationError("Insufficient stock for the operation.")
        self.Quantity += quantity
        self.save()
