from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_read_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "TCC DevSecOps API"}


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_items():
    response = client.get("/items")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["id"] == 1
    assert data[0]["name"] == "Item exemplo"
    assert data[0]["description"] == "Item usado no experimento"


def test_create_item():
    payload = {
        "name": "Novo item",
        "description": "Item criado durante o teste",
    }

    response = client.post("/items", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]