from starlette.testclient import TestClient;
from main import main

client = TestClient(main())

def test_read_main():
  response = client.get("/")
  assert response.status_code == 200
  assert response.json() == {'message': 'Hello Bigger Applications!'}
