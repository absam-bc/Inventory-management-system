import requests
import base64

BASE_URL = "https://world.openfoodfacts.net/api/v3.6/product/"

HEADERS = {
    "Authorization": "Basic " + base64.b64encode(
        b"off:off"
    ).decode("utf-8"),
    "User-Agent": "InventoryManagementSystem/1.0"
}


def get_product(barcode):
    """Fetch product details from OpenFoodFacts using a barcode."""
    if not isinstance(barcode, str) or not barcode.strip():
        return {"error": "A valid barcode is required"}

    url = f"{BASE_URL}{barcode.strip()}.json"

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15
        )

        response.raise_for_status()
        data = response.json()

        product = data.get("product")

        if not product:
            return {"error": "Product not found"}

        return {
            "barcode": barcode.strip(),
            "name": product.get("product_name") or "Unknown product",
            "brand": product.get("brands") or "Unknown brand",
            "category": product.get("categories") or "Unknown category"
        }

    except requests.Timeout:
        return {"error": "OpenFoodFacts request timed out"}

    except requests.RequestException:
        return {"error": "Could not connect to OpenFoodFacts"}

    except ValueError:
        return {"error": "OpenFoodFacts returned invalid JSON"}