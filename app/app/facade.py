from Procurement import Supplier, PurchaseOrder
from Inventory import Product
from Sales.models import Sales
from Inventory.models import Product, Store

class Facade():

    def __init__(self):
        self.sales = Sales.objects.all()
        self.stores = Store.objects.all()
        self.products = Product.objects.all()

    def RestockProduct(self, productId):

        """
        Triggers a purchase order if the product's stock is below its reorder level.
        Args:
            productId: The product ID to check.
        Returns:
            A message about what happened.
        """

        try:
            product = Product.objects.get(ProductId=productId)# Fetch the product
            currentStock = product.GetStockLevel()# Get the current stock level for the product

            if currentStock < product.ReorderLevel: # Check if the stock is below the reorder level
                # Get the supplier associated with the product
                supplier = Supplier.objects.get(SupplierId=product.SupplierId.SupplierId)

                if not supplier.exists(): # If no supplier exists, return a message
                    return f"No supplier found for product ID {productId}."

                # Calculate the reorder quantity and total amount
                reorderQuantity = product.ReorderLevel - currentStock
                totalAmount = reorderQuantity * product.Price
                # Create a new purchase order with "Pending" status
                purchaseOrder = PurchaseOrder.CreatePurchaseOrder(
                    product=product,
                    totalAmount=totalAmount,
                    orderStatus="Pending",
                    supplierId=supplier
                )

                # Return a success message with purchase order details
                return f"Purchase order {purchaseOrder.PurchaseOrderId} created for product ID {productId} with quantity {reorderQuantity}."

            else:# If stock is sufficient, return a message indicating no action is needed
                return f"Stock level ({currentStock}) for product ID {productId} is sufficient. No purchase order needed."

        except Product.DoesNotExist:# Handle the case where the product does not exist in the database
            return f"Product ID {productId} does not exist."

        except Exception as e:# Handle any other unexpected errors and return the error message
            return f"Error triggering purchase order: {str(e)}"


    def GetStorePerformance(self, start_date=None, end_date=None):
        """
        Retrieves sales data for graphing performance by stores and products.
        
        Args:
            start_date (datetime.date, optional): Start date to filter sales data.
            end_date (datetime.date, optional): End date to filter sales data.
        
        Returns:
            dictionary: Contains store-wise and product-wise sales performance data.
        """
        try:
            from django.db.models import Sum
            # Initialise sales queryset
            sales_queryset = self.sales

            # Filter sales data by start date if provided
            if start_date:
                sales_queryset = sales_queryset.filter(DateOfSale__gte=start_date)

            # Filter sales data by end date if provided
            if end_date:
                sales_queryset = sales_queryset.filter(DateOfSale__lte=end_date)

            # Aggregate sales data by product
            product_sales = (
                sales_queryset.values("StoreId__StoreName", "ProductId__ProductName")# Group by store and product
                .annotate(TotalSales=Sum("TotalAmount"))# Calculate total sales per product
                .order_by("ProductId__ProductName")# Sort results by product name
            )

            # Aggregate total sales grouped by store
            store_sales = (
                sales_queryset.values("StoreId__StoreName")# Group by store name
                .annotate(TotalSales=Sum("TotalAmount")) # Calculate total sales per store
                .order_by("StoreId__StoreName")# Sort results by store name
            )

            # Return aggregated sales data as a dictionary
            return {"store_sales": list(store_sales), "product_sales": list(product_sales)}

        except Exception as e: # Raise a ValueError with the error message in case of failure
            raise ValueError(f"Error generating sales performance graph: {str(e)}")
