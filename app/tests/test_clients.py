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
  response = client.get("/clients", headers={"token": "hailhydra"});
  assert response.status_code == 403;
  assert response.json() == {'detail': 'Not authenticated'}

# test valid token
def test_listClients():
  header = {'Authorization': 'Bearer {}'.format(token)}
  response = client.get("/clients", headers=header, json={"showDeleted": True});
  assert response.status_code == 200;
  assert type(response.json()) == type([]);

# test to find a client
def test_listClient():
  header = {'Authorization': 'Bearer {}'.format(token)}
  response = client.get("/clients", headers=header, json={"uid": "60e5ea24e326417eb2a0297b"});
  assert response.status_code == 200;
  assert type(response.json()) == type([]);

# test to find a client not ind DB
def test_listClientNotInDB():
  header = {'Authorization': 'Bearer {}'.format(token)}
  response = client.get("/clients/20e5ea24e326417eb2a0297f", headers=header);
  assert response.status_code == 200;
  assert response.json() == [];