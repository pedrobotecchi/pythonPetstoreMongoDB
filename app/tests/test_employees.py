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
def test_listEmployees_bad_token():
  response = client.get("/employees", headers={"token": "hailhydra"});
  assert response.status_code == 403;
  assert response.json() == {'detail': 'Not authenticated'}

# should catch the token
def test_login():
  response = client.post("/employees/authenticated", json={"user":"test", "password":"test"});
  assert response.status_code == 200;

# test valid token
def test_listEmployees():
  header = {'Authorization': 'Bearer {}'.format(token)}
  response = client.get("/employees", headers=header, json={"showDeleted": True});
  assert response.status_code == 200;
  assert type(response.json()) == type([]);

# test to find a employee
def test_listEmployee():
  header = {'Authorization': 'Bearer {}'.format(token)}
  response = client.get("/employees", headers=header, json={"uid": "60e5ea24e326417eb2a0297b"});
  assert response.status_code == 200;
  assert type(response.json()) == type([]);

# test to find a employee not ind DB
def test_listEmployeeNotInDB():
  header = {'Authorization': 'Bearer {}'.format(token)}
  response = client.get("/employees/60e5ea24e326417eb2a0297f", headers=header);
  assert response.status_code == 200;
  assert response.json() == [];