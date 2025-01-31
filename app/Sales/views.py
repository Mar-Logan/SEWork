from django.http import JsonResponse
from django.shortcuts import render

from app.facade import Facade  # Importing the Facade layer to handle business logic.


def GetStorePerformance(request):

    # Handles requests for sales performance data and returns it as a JSON response.

    facade = Facade()  # Instantiates the Facade class to access sales performance logic.
    
    start_date = request.GET.get("start_date")  # Retrieves the optional 'start_date' from query parameters.
    end_date = request.GET.get("end_date")  # Retrieves the optional 'end_date' from query parameters.

    sales_data = facade.GetSalesPerformanceGraph(start_date, end_date)  # Fetches sales performance data filtered by dates.

    return JsonResponse(
        {
            "store_sales": sales_data["store_sales"],  # Includes store-wise sales performance.
            "product_sales": sales_data["product_sales"],  # Includes product-wise sales performance.
        }
    )