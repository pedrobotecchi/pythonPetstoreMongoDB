from fastapi import APIRouter
from fastapi.param_functions import Depends
from pymongo import MongoClient;
from starlette.responses import JSONResponse;
from auth.auth import AuthHandler;
from models.dogs import *;

router = APIRouter();

auth_handler = AuthHandler();

client = MongoClient('mongodb://localhost:27017/');
mongo = client['petstore'];

# Get all dogs
@router.get('/dogs')
async def get_all_dogs(body: DogBody, token = Depends(auth_handler.auth_wrapper)):
    dogs = mongo.dogs;
    output = [];
    query = { '$or' : [ {'deleted': { '$exists': False}} , { 'deleted': None }] } if not body.showDeleted else {};
    for q in dogs.find(query):
        id = str(q['_id']);
        output.append({ 'id': id ,'name': q['name'], 'breed': q['breed'], 'furr': q['furr'], 'size': q['size'], 'uid_client': q['uid_client'] });

    return (output);

# Get an specific dog
@router.get('/dogs/{uid}')
async def get_dog(uid: OID, token = Depends(auth_handler.auth_wrapper)):
    dogs = mongo.dogs;
    output = [];
    for q in dogs.find({ '_id': uid }):
        id = str(q['_id']);
        output.append({ 'id': id ,'name': q['name'], 'breed': q['breed'], 'furr': q['furr'], 'size': q['size'], 'uid_client': q['uid_client'] });

    return (output);

# Post a dog
@router.post('/dogs/insert', response_model=Dog)
async def post_client(dogInfo : Dog, token = Depends(auth_handler.auth_wrapper)):
    dog = mongo.dogs;
    foundDogInDB = await search_dog(dogInfo.cpf, dogInfo.uid_client);
    if(not foundDogInDB):
        dog.insert_one(dogInfo.__dict__)
        return dogInfo;

    return JSONResponse(status_code=200, content={"Error": "Employee already inserted"})

# Update an specific dog
@router.patch('/dogs', response_model=Dog)
async def update_client(dogInfo : Dog, token = Depends(auth_handler.auth_wrapper)):
    dogs = mongo.dogs;
    foundDogInDB = await search_dog_byID(dogInfo.uid);
    if(foundDogInDB):
        dogs.update_one({ '_id': dogInfo.uid},{ "$set" : dogInfo.__dict__});
        return dogInfo;

    return JSONResponse(status_code=200, content={"Error": "Employee not found in DB inserted"})

# Remove an specific client
@router.delete('/dogs')
async def delete_dog(body: DogBody, token = Depends(auth_handler.auth_wrapper)):
    dogs = mongo.dogs;
    foundDogInDB = await search_dog_byID(body.uid);
    if(foundDogInDB):
        dogs.update_one({ '_id': body.uid }, { "$set": { 'deleted': True } });
        return True;

    return JSONResponse(status_code=200, content={"Error": "Employee not found in DB inserted"})

# Helper functions
async def search_dog(dogName, uid_client) :
    dogs = mongo.dogs;
    output = False;
    for q in dogs.find({ 'name': dogName, "uid_client": uid_client }):
        output = True;

    return output;

# Helper functions
async def search_dog_byID(uid) :
    dogs = mongo.dogs;
    output = False;
    for q in dogs.find({ '_id': uid }):
        output = True;

    return output;

async def get_dogs_byClient(uid_client):
    dogs = mongo.dogs;
    output = [];

    for q in dogs.find({ 'uid_client': uid_client }):
        id = str(q['_id']);
        output.append({ 'id': id ,'name': q['name'], 'breed': q['breed'], 'furr': q['furr'], 'size': q['size'], 'uid_client': q['uid_client'] });

    return output;

async def delete_dogs_byClient(uid_client) :
    dogs = mongo.dogs;

    for q in dogs.find({ 'uid_client': uid_client }):
        id = str(q['_id']);
        await delete_dog(id);


    return True;