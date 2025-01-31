from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from app.facade import Facade
from Inventory.models import Product
import json


@csrf_exempt
def RestockProduct(request):
    """
    Function-based view to trigger a purchase order for a product.
    :param request: The HTTP request object.
    :return: A JsonResponse indicating the success or failure of the operation.
    """
    if request.method == "POST":
        try:
            # Parse the request body to get product ID
            body = json.loads(request.body)
            product_id = body.get("productId")
            if not product_id:
                return JsonResponse({"error": "Product ID is required."}, status=400)

            # Instantiate the facade for business logic
            facade = Facade()
            # Call the TriggerPurchaseOrder function and get the result message
            result_message = facade.RestockProduct(productId=int(product_id))
            # Return success response with message
            return JsonResponse({"message": result_message}, status=200)



        except Product.DoesNotExist:                                           # Handle case when the product does not exist
            return JsonResponse(
                {"error": f"Product ID {product_id} does not exist."}, status=404
            )
        except json.JSONDecodeError:                                                # Handle case for invalid JSON format
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:                                                           # General error handling for any other exceptions
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
        


    # If not POST, return method not allowed
    return JsonResponse({"error": "Only POST method is allowed."}, status=405)