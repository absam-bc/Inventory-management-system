import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "inventory.json"


def load_inventory():
    """Load inventory products from the JSON file."""
    if not DATA_FILE.exists():
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            inventory = json.load(file)

        if not isinstance(inventory, list):
            raise ValueError("Inventory data must be a JSON list.")

        return inventory

    except json.JSONDecodeError as error:
        raise ValueError("Inventory JSON file contains invalid data.") from error


def save_inventory(inventory):
    """Save inventory products to the JSON file."""
    if not isinstance(inventory, list):
        raise ValueError("Inventory must be a list.")

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(inventory, file, indent=4)
        file.write("\n")