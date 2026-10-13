import requests

BASE_URL = "http://127.0.0.1:5000"


def show_response(response):
    try:
        print(response.json())
    except ValueError:
        print("The server returned an invalid response.")

    if not response.ok:
        print(f"Request failed: HTTP {response.status_code}")


def view_inventory():
    response = requests.get(f"{BASE_URL}/inventory", timeout=10)
    show_response(response)


def add_product():
    product = {
        "name": input("Product name: ").strip(),
        "price": float(input("Price: ")),
        "quantity": int(input("Stock quantity: ")),
        "barcode": input("Barcode: ").strip(),
        "category": input("Category: ").strip()
    }

    response = requests.post(
        f"{BASE_URL}/inventory",
        json=product,
        timeout=10
    )
    show_response(response)


def update_product():
    product_id = input("Product ID: ").strip()

    response = requests.get(
        f"{BASE_URL}/inventory/{product_id}",
        timeout=10
    )

    if not response.ok:
        show_response(response)
        return

    product = response.json()
    updates = {}

    print("Leave a field blank to keep its current value.")

    for field in ["name", "price", "quantity", "barcode", "category"]:
        value = input(
            f"{field.capitalize()} [{product[field]}]: "
        ).strip()

        if not value:
            continue

        if field == "price":
            updates[field] = float(value)
        elif field == "quantity":
            updates[field] = int(value)
        else:
            updates[field] = value

    if not updates:
        print("No changes made.")
        return

    response = requests.patch(
        f"{BASE_URL}/inventory/{product_id}",
        json=updates,
        timeout=10
    )
    show_response(response)


def delete_product():
    product_id = input("Product ID to delete: ").strip()

    confirmation = input(
        f"Delete product {product_id}? (y/n): "
    ).strip().lower()

    if confirmation != "y":
        print("Deletion cancelled.")
        return

    response = requests.delete(
        f"{BASE_URL}/inventory/{product_id}",
        timeout=10
    )
    show_response(response)


def search_product():
    barcode = input("Enter barcode to search: ").strip()

    if not barcode:
        print("Barcode cannot be empty.")
        return

    response = requests.get(
        f"{BASE_URL}/products/{barcode}",
        timeout=20
    )

    if not response.ok:
        show_response(response)
        return

    product = response.json()

    print("\n=== PRODUCT FOUND ===")
    print(f"Barcode: {product.get('barcode', barcode)}")
    print(f"Name: {product.get('name', 'Unknown product')}")
    print(f"Category: {product.get('category', 'Unknown category')}")

    choice = input(
        "\nAdd this product to inventory? (y/n): "
    ).strip().lower()

    if choice != "y":
        print("Product was not added.")
        return

    try:
        price = float(input("Selling price: "))
        quantity = int(input("Stock quantity: "))
    except ValueError:
        print("Enter a valid price and whole-number quantity.")
        return

    response = requests.post(
        f"{BASE_URL}/inventory/import/{barcode}",
        json={
            "price": price,
            "quantity": quantity
        },
        timeout=20
    )

    show_response(response)


def main():
    while True:
        print("\n=== INVENTORY MANAGEMENT SYSTEM ===")
        print("1. View inventory")
        print("2. Add product")
        print("3. Update product")
        print("4. Delete product")
        print("5. Search/import product by barcode")
        print("6. Exit")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                view_inventory()
            elif choice == "2":
                add_product()
            elif choice == "3":
                update_product()
            elif choice == "4":
                delete_product()
            elif choice == "5":
                search_product()
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Choose an option from 1 to 6.")

        except requests.exceptions.Timeout:
            print("The request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            print("Cannot connect. Make sure Flask is running.")
        except requests.exceptions.RequestException as error:
            print(f"Request error: {error}")
        except ValueError:
            print("Invalid input. Check the price or quantity.")


if __name__ == "__main__":
    main()