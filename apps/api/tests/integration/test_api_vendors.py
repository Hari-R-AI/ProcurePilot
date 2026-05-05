"""Integration tests for Vendor API endpoints."""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from app.main import create_app

@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)

def test_create_vendor(client: TestClient):
    """Test creating a new vendor via API."""
    vendor_data = {
        "legal_name": "Test Acme Private Limited",
        "trade_name": "Test Acme",
        "entity_type": "Private Limited",
        "gstin": "27AAAAA0000A1Z5",
        "pan_number": "AAAAA0000A",
        "msme_registered": False,
        "contact_email": "test@acme.example.com",
        "contact_phone": "+91-9876543210",
        "address": "Mumbai, MH"
    }

    response = client.post("/api/v1/vendors", json=vendor_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert data["legal_name"] == vendor_data["legal_name"]
    assert data["gstin"] == vendor_data["gstin"]
    assert "id" in data
    assert data["compliance_status"] == "VERIFIED"

def test_create_vendor_invalid_gstin(client: TestClient):
    """Test vendor creation with mismatched GSTIN-PAN relationship."""
    vendor_data = {
        "legal_name": "Test Acme 2",
        "entity_type": "Private Limited",
        "gstin": "27BBBBB0000A1Z5",
        "pan_number": "AAAAA0000A",  # Mismatch
        "msme_registered": False,
        "contact_email": "test2@acme.example.com",
        "address": "Mumbai, MH"
    }

    response = client.post("/api/v1/vendors", json=vendor_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "GSTIN characters 3-12 must match the PAN" in response.json()["error"]["detail"]

def test_list_vendors(client: TestClient):
    """Test listing vendors."""
    response = client.get("/api/v1/vendors")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "vendors" in data
    assert "total" in data
    assert isinstance(data["vendors"], list)
