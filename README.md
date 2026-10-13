# Inventory Management System

A Flask-based inventory management application for a small retail business.

## Features

- Create, view, update, and delete inventory products.
- Store product data in a JSON file.
- Search OpenFoodFacts using product barcodes.
- Import external products into inventory.
- Validate input and handle API errors.
- Run automated tests with pytest.

## Technologies

- Python
- Flask
- Requests
- JSON
- Pytest
- OpenFoodFacts API

## Project Structure

    Inventory-management-system/
    ├── app.py
    ├── api_service.py
    ├── cli.py
    ├── data_manager.py
    ├── data/
    │   └── inventory.json
    ├── tests/
    │   ├── conftest.py
    │   ├── test_app.py
    │   └── test_api_service.py
    ├── requirements.txt
    ├── .gitignore
    └── README.md

## Installation

Clone your repository and enter its directory:

    git clone <YOUR_GITHUB_REPOSITORY_URL>
    cd Inventory-management-system

Create and activate a virtual environment:

    python3 -m venv venv
    source venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with your actual GitHub repository URL.

## Running the Application

Start the Flask server:

    python app.py

The API runs at http://127.0.0.1:5000.

Open a second terminal, activate the virtual environment, and run the CLI:

    cd ~/Inventory-management-system
    source venv/bin/activate
    python cli.py

Keep the Flask server running while using the CLI.

## Product Fields

Every product contains:

- `id`: Unique product identifier.
- `name`: Product name.
- `price`: Selling price.
- `quantity`: Available stock.
- `barcode`: Product barcode.
- `category`: Product category.

Inventory is persisted in `data/inventory.json`.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check the API |
| GET | `/inventory` | List all products |
| GET | `/inventory/<id>` | Retrieve a product |
| POST | `/inventory` | Add a product |
| PATCH | `/inventory/<id>` | Update a product |
| DELETE | `/inventory/<id>` | Delete a product |
| GET | `/products/<barcode>` | Search OpenFoodFacts |
| POST | `/inventory/import/<barcode>` | Import a product |

## Example: Add a Product

Send a POST request to `/inventory` with this JSON body:

    {
      "name": "Whole Wheat Bread",
      "price": 80.0,
      "quantity": 15,
      "barcode": "56797432",
      "category": "Bakery"
    }

## Example: Update Stock

Send a PATCH request to `/inventory/1` with:

    {
      "quantity": 25
    }

## Example: Import a Product

Send a POST request to `/inventory/import/3274080005003` with:

    {
      "price": 120.0,
      "quantity": 10
    }

The application retrieves product details from OpenFoodFacts. The selling price and stock quantity are supplied by the user.

## Running Tests

Activate the virtual environment and run:

    python -m pytest -v

The test suite covers API operations, validation, barcode lookup, importing products, and simulated external API failures. The tests use mocks for external requests and do not require a live API connection.

## Error Handling

The application handles invalid product data, negative prices, invalid quantities, duplicate barcodes, missing products, connection errors, and request timeouts.

## External API

OpenFoodFacts: https://world.openfoodfacts.org/

Product information and API availability may vary.

## Version Control

Use Git branches to develop features, commit changes, and merge completed work into the main branch after review.

## License

Created for educational purposes.
