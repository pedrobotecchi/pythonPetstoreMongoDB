from fastapi import APIRouter;
from fastapi.param_functions import Depends;
from pymongo import MongoClient;
from starlette.responses import JSONResponse;
from .dogs import get_dogs_byClient, delete_dogs_byClient;
from auth.auth import AuthHandler;
from models.clients import *;

router = APIRouter();

auth_handler = AuthHandler();

client = MongoClient('mongodb://localhost:27017/');
mongo = client['petstore'];

# Get all clients
@router.get('/clients')
async def get_all_clients(body : ClientBody, token = Depends(auth_handler.auth_wrapper)):
    clients = mongo.clients;
    output = [];
    query = { '$or' : [ {'deleted': { '$exists': False}} , { 'deleted': None }] } if not body.showDeleted else {};
    for q in clients.find(query):
        id = str(q['_id']);
        dogs = await get_dogs_byClient(id);
        print('type of dogs', type(dogs));
        output.append({ 'id': id ,'name': q['name'], 'cpf': q['cpf'], 'address': q['address'], 'phone': q['phone'], 'dogs': dogs });

    return (output);

# Get an specific client
@router.get('/clients/{uid}')
async def get_client(uid: OID, token = Depends(auth_handler.auth_wrapper)):
    clients = mongo.clients;
    output = [];
    for q in clients.find({ '_id': uid }):
        id = str(q['_id']);
        dogs = await get_dogs_byClient(id);
        output.append({ 'id': id ,'name': q['name'], 'cpf': q['cpf'], 'address': q['address'], 'phone': q['phone'], 'dogs' : dogs });

    return (output);

# Post a client
@router.post('/clients/insert', response_model=Client)
async def post_client(clientInfo : Client, token = Depends(auth_handler.auth_wrapper)):
    client = mongo.clients;
    foundClientInDB = await search_client_byCPF(clientInfo.cpf);
    if(not foundClientInDB):
        client.insert_one(clientInfo.__dict__)
        return clientInfo;

    return JSONResponse(status_code=200, content={"Error": "Employee already inserted"})

# Update an specific client
@router.patch('/clients', response_model=Client)
async def update_client(clientInfo : Client, token = Depends(auth_handler.auth_wrapper)):
    clients = mongo.clients;
    foundClientInDB = await search_client_byID(clientInfo.uid);
    if(foundClientInDB):
        clients.update_one({ '_id': clientInfo.uid},{ "$set" : clientInfo.__dict__});
        return clientInfo;

    return JSONResponse(status_code=200, content={"Error": "Employee not found in DB inserted"})

# Remove an specific client
@router.delete('/clients')
async def delete_employee(body: ClientBody, token = Depends(auth_handler.auth_wrapper)):
    clients = mongo.clients;
    foundClientInDB = await search_client_byID(body.uid);
    if(foundClientInDB):
        clients.update_one({ '_id': body.uid }, { "$set": { 'deleted': True } });
        delete_dogs_byClient(body.uid);

        return True;

    return JSONResponse(status_code=200, content={"Error": "Employee not found in DB inserted"})

# Helper functions
async def search_client_byCPF(cpf) :
    clients = mongo.clients;
    output = False;
    for q in clients.find({ 'cpf': cpf }):
        output = True;

    return output;

# Helper functions
async def search_client_byID(uid) :
    clients = mongo.clients;
    output = False;
    for q in clients.find({ '_id': uid }):
        output = True;

    return output;

