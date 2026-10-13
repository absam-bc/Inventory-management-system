import json
import pytest
import app as inventory_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    inventory_file = tmp_path / "inventory.json"
    inventory_file.write_text("[]", encoding="utf-8")

    def load_test_inventory():
        with open(inventory_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def save_test_inventory(items):
        with open(inventory_file, "w", encoding="utf-8") as file:
            json.dump(items, file, indent=4)

    monkeypatch.setattr(
        inventory_app, "load_inventory", load_test_inventory
    )
    monkeypatch.setattr(
        inventory_app, "save_inventory", save_test_inventory
    )

    inventory_app.app.config["TESTING"] = True

    with inventory_app.app.test_client() as test_client:
        yield test_client


def sample_product():
    return {
        "name": "Milk",
        "price": 350,
        "quantity": 10,
        "barcode": "123456789",
        "category": "Dairy"
    }


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200


def test_get_empty_inventory(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    assert response.get_json() == []


def test_add_product(client):
    response = client.post("/inventory", json=sample_product())

    assert response.status_code == 201
    assert response.get_json()["name"] == "Milk"
    assert response.get_json()["id"] == 1


def test_get_existing_product(client):
    client.post("/inventory", json=sample_product())

    response = client.get("/inventory/1")

    assert response.status_code == 200
    assert response.get_json()["barcode"] == "123456789"


def test_get_missing_product(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404


def test_reject_negative_price(client):
    product = sample_product()
    product["price"] = -1

    response = client.post("/inventory", json=product)
    assert response.status_code == 400


def test_reject_negative_quantity(client):
    product = sample_product()
    product["quantity"] = -1

    response = client.post("/inventory", json=product)
    assert response.status_code == 400


def test_reject_duplicate_barcode(client):
    client.post("/inventory", json=sample_product())

    product = sample_product()
    product["name"] = "Another milk"

    response = client.post("/inventory", json=product)
    assert response.status_code == 409


def test_patch_product(client):
    client.post("/inventory", json=sample_product())

    response = client.patch(
        "/inventory/1",
        json={"quantity": 25}
    )

    assert response.status_code == 200
    assert response.get_json()["quantity"] == 25
    assert response.get_json()["name"] == "Milk"


def test_patch_missing_product(client):
    response = client.patch(
        "/inventory/999",
        json={"quantity": 25}
    )
    assert response.status_code == 404


def test_delete_product(client):
    client.post("/inventory", json=sample_product())

    response = client.delete("/inventory/1")

    assert response.status_code == 200
    assert client.get("/inventory").get_json() == []


def test_delete_missing_product(client):
    response = client.delete("/inventory/999")
    assert response.status_code == 404


def test_barcode_lookup_success(client, monkeypatch):
    monkeypatch.setattr(
        inventory_app,
        "get_product",
        lambda barcode: {
            "barcode": barcode,
            "name": "Test product",
            "brand": "Test brand",
            "category": "Test category"
        }
    )

    response = client.get("/products/123456789")

    assert response.status_code == 200
    assert response.get_json()["name"] == "Test product"


def test_barcode_lookup_failure(client, monkeypatch):
    monkeypatch.setattr(
        inventory_app,
        "get_product",
        lambda barcode: {"error": "Product not found"}
    )

    response = client.get("/products/000000000")

    assert response.status_code == 404


def test_import_product(client, monkeypatch):
    monkeypatch.setattr(
        inventory_app,
        "get_product",
        lambda barcode: {
            "barcode": barcode,
            "name": "Imported cereal",
            "brand": "Test brand",
            "category": "Breakfast"
        }
    )

    response = client.post(
        "/inventory/import/123456789",
        json={"price": 200, "quantity": 5}
    )

    assert response.status_code == 201
    assert response.get_json()["product"]["name"] == "Imported cereal"

    inventory = client.get("/inventory").get_json()
    assert len(inventory) == 1
    assert inventory[0]["barcode"] == "123456789"


def test_import_duplicate_barcode(client, monkeypatch):
    client.post("/inventory", json=sample_product())

    monkeypatch.setattr(
        inventory_app,
        "get_product",
        lambda barcode: {
            "barcode": barcode,
            "name": "Milk",
            "brand": "Test brand",
            "category": "Dairy"
        }
    )

    response = client.post(
        "/inventory/import/123456789",
        json={"price": 200, "quantity": 5}
    )

    assert response.status_code == 409