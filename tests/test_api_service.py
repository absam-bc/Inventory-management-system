import requests
from unittest.mock import Mock, patch

from api_service import get_product


@patch("api_service.requests.get")
def test_get_product_success(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {
        "product": {
            "product_name": "Milk",
            "brands": "Example Brand",
            "categories": "Dairy"
        }
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = get_product("123456789")

    assert result["name"] == "Milk"
    assert result["brand"] == "Example Brand"
    assert result["category"] == "Dairy"
    mock_get.assert_called_once()


@patch("api_service.requests.get")
def test_product_not_found(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {"status": 0}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = get_product("999999999")

    assert result == {"error": "Product not found"}


@patch("api_service.requests.get")
def test_request_timeout(mock_get):
    mock_get.side_effect = requests.Timeout

    result = get_product("123456789")

    assert result == {
        "error": "OpenFoodFacts request timed out"
    }


@patch("api_service.requests.get")
def test_connection_error(mock_get):
    mock_get.side_effect = requests.ConnectionError

    result = get_product("123456789")

    assert result == {
        "error": "Could not connect to OpenFoodFacts"
    }


def test_empty_barcode():
    result = get_product("")

    assert result == {
        "error": "A valid barcode is required"
    }


def test_invalid_barcode_type():
    result = get_product(None)

    assert result == {
        "error": "A valid barcode is required"
    }
