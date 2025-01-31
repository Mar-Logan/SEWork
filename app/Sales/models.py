from django.db import models
from Inventory.models import Store, Product
from HR.models import Staff

class Sales(models.Model):

    SalesId = models.AutoField(primary_key=True, unique=True)            # Primary key for the sales record
    PaymentMethod = models.CharField(max_length=200)                    # Payment method used for the sale
    TotalAmount = models.DecimalField(max_digits=15, decimal_places=2)  # Total amount for the sale

    StoreId = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='sales')   # ForeignKey to Store model
    ProductId = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='sales', null=True)  # ForeignKey to Product model

    # ForeignKey to Staff model, representing the staff member handling the sale
    StaffId = models.ForeignKey(        
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sales'
    )
    SaleDate = models.DateField(auto_now_add=True)    # Date when the sale occurred

    def __str__(self):  # String representation of the sale with its ID, total amount, and store name
        return f"Id: {self.SalesId} - Total: {self.TotalAmount} - Store: {self.StoreId.StoreName}"

    def GetSalesData(self):
        """
        Returns the sales record data as a dictionary, including the sale's ID, payment method, total amount, store name,
        staff member handling the sale (if available), and the date of sale.
        """
        return {
            "SalesId": self.SalesId,                # Sale's unique identifier
            "PaymentMethod": self.PaymentMethod,    # Payment method used for the sale
            "TotalAmount": self.TotalAmount,        # Total value of the sale   
            "Store": self.StoreId.StoreName,        # Name of the store
            "Staff": self.StaffId.StaffName if self.StaffId else None,      # Name of the staff handling the sale, if available
            "SaleDate": self.SaleDate,      # Date when the sale was made
        }

    def CalculateTotalSales(self, start_date=None, end_date=None):
        """
        Calculates the total sales amount within the specified date range.
        start_date: Optional start date for filtering sales (datetime.date).
        end_date: Optional end date for filtering sales (datetime.date).
        """
        from django.db.models import Sum    # Import aggregate function for summing values

    
        sales_queryset = Sales.objects.all() # Start with all sales records

        if start_date:   # If start_date is provided, filter sales from that date onward
            sales_queryset = sales_queryset.filter(SaleDate__gte=start_date)


        if end_date:     # If end_date is provided, filter sales up until that date
            sales_queryset = sales_queryset.filter(SaleDate__lte=end_date)

        # Aggregate sales data and sum the TotalAmount for the filtered date range
        total_sales = sales_queryset.aggregate(TotalSales=Sum("TotalAmount"))

        # Return the total sales amount or 0 if no sales are found
        return total_sales["TotalSales"] or 0



    def GetSalesGraph(self, start_date=None, end_date=None):
        """
        Generates sales data for a graph based on the given date range.
        start_date: Optional start date for filtering sales (datetime.date).
        end_date: Optional end date for filtering sales (datetime.date).
        """
        from django.db.models import Sum    # Import aggregate function to sum total sales

        sales_queryset = Sales.objects.all()    # Start with all sales records

        if start_date:   # If start_date is provided, filter sales from that date onward
            sales_queryset = sales_queryset.filter(SaleDate__gte=start_date)


        if end_date:    # If end_date is provided, filter sales up until that date
            sales_queryset = sales_queryset.filter(SaleDate__lte=end_date)

        sales_summary = (    # Aggregate sales data by date, summing the total sales for each day
            sales_queryset

            .values("SaleDate")       # Group by the date of sale
            .annotate(TotalSales=Sum("TotalAmount"))     # Calculate the sum of TotalAmount for each date
            .order_by("SaleDate") # Order the results by the date of sale
        )

        return list(sales_summary)  # Returns a list of dictionaries for graph plotting


