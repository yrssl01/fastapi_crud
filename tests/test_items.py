from fastapi.testclient import TestClient
from src.main import app


client = TestClient(app)


def test_read_item():
    response = client.get('/items/1')
    assert response.status_code == 200
    assert response.json() == {
        'id': 1,
        'name': 'Hello',
        'description': 'World'
    }


def test_read_bad_item():
    response = client.get('/items/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Item not found'}


def test_create_item():
    response = client.post(
        '/items/',
        json={'name': 'Item1', 'description': 'New item created'}
    )
    assert response.status_code == 201
    assert response.json() == {
        'name': 'Item1', 
        'description': 'New item created',
        'id': 2
    }





