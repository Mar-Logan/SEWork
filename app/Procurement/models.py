from django.db import models
from Inventory.models import Product
from django.db.models import Sum, Avg, Count
from datetime import datetime, timedelta

class Supplier(models.Model):
    SupplierId = models.AutoField(primary_key=True, unique=True)    # Unique ID for the supplier.
    SupplierName = models.CharField(max_length=200)                 # Name of the supplier

    ContactDetails = models.CharField(max_length=200)               # Contact information for the supplier
    Location = models.CharField(max_length=200)                     # Location of the supplier
    ContractTerms = models.CharField(max_length=200)                # Terms of the contract with the supplier


    def __str__(self):  # String representation of the supplier, displaying the name and location
        return f"{self.SupplierName} - {self.Location}"


    def GetSupplierProducts(self):  # Retrieves all products associated with the supplier.
        return Product.objects.filter(SupplierId=self.SupplierId)


    def GetSupplierPerformance(self, dateRange=30):
        """
        Analyses the supplier's performance based on delivered orders over a specified period.
        :param dateRange: The number of days to consider for the analysis.
        :return: Performance metrics.
        """

        endDate = datetime.now()        # Calculate the start and end dates for the analysis
        startDate = endDate - timedelta(days=dateRange)


        # Filter purchase orders associated with this supplier and within the date range
        orders = PurchaseOrder.objects.filter(

            # Match products supplied by this supplier
            ProductId__SupplierId=self.SupplierId,

            # Restrict to the specified date range
            DeliveryDate__range=[startDate, endDate],
            OrderStatus="Delivered",    # Only include delivered orders
        )


        # Aggregate total order amount and count the number of delivered orders
        totalAmount = orders.aggregate(total=Sum("FullCost"))["total"] or 0
        totalOrders = orders.count()


        performance = { # Compile performance metrics into a dictionary
            "TotalDeliveredOrders": totalOrders,
            "TotalDeliveredAmount": totalAmount,
            "AverageOrderValue": totalAmount / totalOrders if totalOrders > 0 else 0,
        }
        return performance


    def EditSupplierData(self, **kwargs):
        """
        Updates the supplier's data with new values for specified fields

        :param kwargs: Dictionary of field names and their new values
        'SupplierName', 'ContactDetails', 'Location', 'ContractTerms'
        
        :raises ValueError: If an invalid field is provided in kwargs
        """
        allowed_fields = {"SupplierName", "ContactDetails", "Location", "ContractTerms"}

        for field, value in kwargs.items(): # Iterate through each field and value provided in kwargs

            if field not in allowed_fields:# Check if the field is in the list of allowed fields
                raise ValueError(f"Invalid field: {field}")
            
            # Update the field with the new value
            setattr(self, field, value)

        self.save()# Save the updated supplier data



class PurchaseOrder(models.Model):
    PurchaseOrderId = models.AutoField(primary_key=True, unique=True)       # A unique ID for each purchase order
    FullCost = models.DecimalField(max_digits=10, decimal_places=2)      # The total monetary amount of the purchase order

    ProductId = models.ForeignKey(Product, on_delete=models.CASCADE)         # Reference to the product associated with the purchase order
    OrderDate = models.DateField(auto_now_add=True)                     # The date when the order was created
    DeliveryDate = models.DateField(blank=True, null=True)              # The date when the order was delivered
    OrderStatus = models.CharField(max_length=200)                      # The status of the order



    def __str__(self):  # Returns a readable string representation of the purchase order
        return f"Id:{self.PurchaseOrderId} - Contains:{self.ProductId.ProductName} - Amount:{self.FullCost} - Status:{self.OrderStatus}"

    @classmethod
    def CreatePurchaseOrder(
        cls, product, totalAmount, deliveryDate, orderStatus="Pending"
    ):
        """
        Creates a new purchase order
        :param product: Product instance to be ordered, totalAmount: Total amount of the purchase.
        :param deliveryDate: Expected delivery date, orderStatus: Status of the order. Default is 'Pending'.
        """

        return cls.objects.create(  # Creates a new purchase order with the provided details
            ProductId=product,
            FullCost=totalAmount,
            DeliveryDate=deliveryDate,
            OrderStatus=orderStatus,
        )
    

    def SetPurchaseOrder(self, **kwargs):
        """
        Updates the purchase order's details.
        :param kwargs: Dictionary of field names and their new values.
        """
        # Updates the purchase order with the provided valid fields
        allowed_fields = {"FullCost", "DeliveryDate", "OrderStatus"}

        for field, value in kwargs.items():
            if field not in allowed_fields:
                raise ValueError(f"Invalid field: {field}")
            
            setattr(self, field, value)
            
        self.save()    # Save the changes to the database


    def GetPurchaseOrderStatus(self): # Retrieves the current status of the purchase order
        return self.OrderStatus


