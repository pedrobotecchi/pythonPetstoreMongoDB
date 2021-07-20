from fastapi import APIRouter;
from fastapi.param_functions import Depends;
from pymongo import MongoClient;
from starlette.responses import JSONResponse;
from auth.auth import AuthHandler;
from models.products import *;

router = APIRouter();

auth_handler = AuthHandler();

client = MongoClient('mongodb://localhost:27017/');
mongo = client['petstore'];

# Get all products
@router.get('/products')
async def get_all_products(body: ProductBody, token = Depends(auth_handler.auth_wrapper)):
    products = mongo.products;
    output = [];
    query = { '$or' : [ {'deleted': { '$exists': False}} , { 'deleted': None }] } if not body.showDeleted else {};
    for q in products.find(query):
        id = str(q['_id']);
        output.append({ 'id': id ,'name': q['name'], 'price': q['price'], 'description': q['description'] });

    return (output);

# Get an specific product
@router.get('/products/{uid}')
async def get_product(uid: OID, token = Depends(auth_handler.auth_wrapper)):
    products = mongo.products;
    output = [];
    for q in products.find({ '_id': uid }):
        id = str(q['_id']);
        output.append({ 'id': id ,'name': q['name'], 'price': q['price'], 'description': q['description'] });

    return (output);

# Post a product
@router.post('/products/insert', response_model=Product)
async def post_product(productInfo : Product, token = Depends(auth_handler.auth_wrapper)):
    products = mongo.products;
    foundProductInDB = await search_product_byName(productInfo.name);
    if(not foundProductInDB):
        products.insert_one(productInfo.__dict__)
        return productInfo;

    return JSONResponse(status_code=200, content={"Error": "Employee already inserted"})

# Update an specific product
@router.patch('/products', response_model=Product)
async def update_product(productInfo : Product, token = Depends(auth_handler.auth_wrapper)):
    products = mongo.products;
    foundProductInDB = await search_product_byID(productInfo.uid);
    if(foundProductInDB):
        products.update_one({ '_id': productInfo.uid},{ "$set" : productInfo.__dict__});
        return productInfo;

    return JSONResponse(status_code=200, content={"Error": "Employee not found in DB inserted"})

# Remove an specific product
@router.delete('/products')
async def delete_product(body: ProductBody, token = Depends(auth_handler.auth_wrapper)):
    products = mongo.products;
    foundProductInDB = await search_product_byID(body.uid);
    if(foundProductInDB):
        products.update_one({ '_id': body.uid }, { "$set": { 'deleted': True } });
        return True;

    return JSONResponse(status_code=200, content={"Error": "Employee not found in DB inserted"})

# Helper functions
async def search_product_byName(name) :
    products = mongo.products;
    output = False;
    for q in products.find({ 'name': name }):
        output = True;

    return output;

# Helper functions
async def search_product_byID(uid) :
    products = mongo.products;
    output = False;
    for q in products.find({ '_id': uid }):
        output = True;

    return output;

