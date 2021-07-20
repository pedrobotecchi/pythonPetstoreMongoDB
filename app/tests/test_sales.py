from starlette.testclient import TestClient;
from main import main
from auth.auth import AuthHandler;

app = main();
client = TestClient(app)

# GET A VALID TOKEN TO USE
def getToken():
    token = AuthHandler().encode_token('teste');
    return token

token = getToken()

# test token not valid
def test_listClients_bad_token():
  response = client.get("/sales", headers={"token": "hailhydra"});
  assert response.status_code == 403;
  assert response.json() == {'detail': 'Not authenticated'}

# test valid token
def test_listSales():
  header = {'Authorization': 'Bearer {}'.format(token)}
  response = client.get("/sales", headers=header, json={"showDeleted": True});
  assert response.status_code == 200;
  assert type(response.json()) == type([]);

# test to find a sales
def test_listSale():
  header = {'Authorization': 'Bearer {}'.format(token)}
  response = client.get("/sales", headers=header, json={"uid": "60e5ea24e326417eb2a0297b"});
  assert response.status_code == 200;
  assert type(response.json()) == type([]);

# test to find a sale not ind DB
def test_listSaleNotInDB():
  header = {'Authorization': 'Bearer {}'.format(token)}
  response = client.get("/sales/20e5ea24e326417eb2a0297f", headers=header);
  assert response.status_code == 200;
  assert response.json() == [];