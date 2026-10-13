from flask import Flask, jsonify, request
import math

from data_manager import load_inventory, save_inventory
from api_service import get_product

app = Flask(__name__)


def validate_item_data(data, require_all=False):
    if not isinstance(data, dict):
        return "A valid JSON object is required"

    allowed_fields = {"name", "price", "quantity", "barcode", "category"}

    if not data:
        return "At least one field must be provided"

    for field in data:
        if field not in allowed_fields:
            return f"Invalid field: {field}"

    if require_all:
        for field in ["name", "price", "quantity", "barcode", "category"]:
            if field not in data:
                return f"Missing field: {field}"

    for field in ["name", "category", "barcode"]:
        if field in data:
            if not isinstance(data[field], str):
                return f"{field.capitalize()} must be a string"
            if field == "name" and not data[field].strip():
                return "Name must not be empty"

    if "price" in data:
        price = data["price"]
        if (
            isinstance(price, bool)
            or not isinstance(price, (int, float))
            or not math.isfinite(price)
            or price < 0
        ):
            return "Price must be a non-negative number"

    if "quantity" in data:
        quantity = data["quantity"]
        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, int)
            or quantity < 0
        ):
            return "Quantity must be a non-negative integer"

    return None


def find_item(item_id):
    inventory = load_inventory()

    for item in inventory:
        if item["id"] == item_id:
            return item

    return None


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Inventory Management System API"
    }), 200


@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(load_inventory()), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = find_item(item_id)

    if item is None:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(item), 200


@app.route("/inventory", methods=["POST"])
def add_item():
    data = request.get_json(silent=True)
    error = validate_item_data(data, require_all=True)

    if error:
        return jsonify({"error": error}), 400

    inventory = load_inventory()
    barcode = data["barcode"].strip()

    if barcode and any(item["barcode"] == barcode for item in inventory):
        return jsonify({"error": "Barcode already exists"}), 409

    new_item = {
        "id": max((item["id"] for item in inventory), default=0) + 1,
        "name": data["name"].strip(),
        "price": data["price"],
        "quantity": data["quantity"],
        "barcode": barcode,
        "category": data["category"].strip()
    }

    inventory.append(new_item)
    save_inventory(inventory)

    return jsonify(new_item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    data = request.get_json(silent=True)
    error = validate_item_data(data)

    if error:
        return jsonify({"error": error}), 400

    inventory = load_inventory()

    for item in inventory:
        if item["id"] == item_id:
            new_barcode = data.get("barcode", item["barcode"]).strip()

            if new_barcode and any(
                other["id"] != item_id and other["barcode"] == new_barcode
                for other in inventory
            ):
                return jsonify({"error": "Barcode already exists"}), 409

            for field, value in data.items():
                item[field] = value.strip() if isinstance(value, str) else value

            save_inventory(inventory)
            return jsonify(item), 200

    return jsonify({"error": "Product not found"}), 404


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    inventory = load_inventory()

    for item in inventory:
        if item["id"] == item_id:
            inventory.remove(item)
            save_inventory(inventory)

            return jsonify({
                "message": "Product deleted successfully",
                "product": item
            }), 200

    return jsonify({"error": "Product not found"}), 404


@app.route("/products/<barcode>", methods=["GET"])
def lookup_product(barcode):
    product = get_product(barcode)

    if "error" in product:
        status_code = (
            404 if "not found" in product["error"].lower() else 502
        )
        return jsonify(product), status_code

    return jsonify(product), 200


@app.route("/inventory/import/<barcode>", methods=["POST"])
def import_product(barcode):
    product = get_product(barcode)

    if "error" in product:
        status_code = (
            404 if "not found" in product["error"].lower() else 502
        )
        return jsonify(product), status_code

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Price and quantity are required"
        }), 400

    import_data = {
        "price": data.get("price"),
        "quantity": data.get("quantity")
    }

    error = validate_item_data(import_data)

    if error:
        return jsonify({"error": error}), 400

    inventory = load_inventory()

    if any(item["barcode"] == barcode for item in inventory):
        return jsonify({"error": "Product is already in inventory"}), 409

    new_item = {
        "id": max((item["id"] for item in inventory), default=0) + 1,
        "name": product["name"],
        "price": data["price"],
        "quantity": data["quantity"],
        "barcode": barcode,
        "category": product.get("category", "Unknown category")
    }

    inventory.append(new_item)
    save_inventory(inventory)

    return jsonify({
        "message": "Product imported successfully",
        "product": new_item
    }), 201


if __name__ == "__main__":
    app.run(debug=True)