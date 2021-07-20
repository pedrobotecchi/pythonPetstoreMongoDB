from fastapi import APIRouter;
from fastapi.param_functions import Depends;
from pymongo import MongoClient;
from starlette.responses import JSONResponse;
from auth.auth import AuthHandler;
from models.sales import *;

router = APIRouter();

auth_handler = AuthHandler();

client = MongoClient('mongodb://localhost:27017/');
mongo = client['petstore'];

# Get all sales
@router.get('/sales')
async def get_all_sales( token = Depends(auth_handler.auth_wrapper)):
    sales = mongo.sales;
    output = [];
    for q in sales.find():
        id = str(q['_id']);
        output.append({ 'id': id ,'amount': q['amount'], 'uid_client': q['uid_client'], 'uid_employee': q['uid_employee'], 'saleDt': q['saleDt'] });

    return (output);

# Get an specific sale
@router.get('/sales/{uid}')
async def get_sale(uid: OID, token = Depends(auth_handler.auth_wrapper)):
    sales = mongo.sales;
    output = [];
    for q in sales.find({ '_id': uid }):
        id = str(q['_id']);
        output.append({ 'id': id ,'amount': q['amount'], 'uid_client': q['uid_client'], 'uid_employee': q['uid_employee'], 'saleDt': q['saleDt'] });

    return (output);

# Post a sale
@router.post('/sales/sell', response_model=Sale)
async def post_sale(saleInfo : Sale, token = Depends(auth_handler.auth_wrapper)):
    sale = mongo.sales;
    sale.insert_one(saleInfo.__dict__)
    return saleInfo;

# Update an specific sale
@router.patch('/sales', response_model=Sale)
async def update_sale(saleInfo : Sale, token = Depends(auth_handler.auth_wrapper)):
    sales = mongo.sales;
    foundSaleInDB = await search_sale_byID(saleInfo.uid);
    if(foundSaleInDB):
        sales.update_one({ '_id': saleInfo.uid},{ "$set" : saleInfo.__dict__});
        return saleInfo;

    return JSONResponse(status_code=200, content={"Error": "Employee not found in DB inserted"})

# Remove an specific sale
@router.delete('/sales')
async def delete_sale(body: SaleBody, token = Depends(auth_handler.auth_wrapper)):
    sales = mongo.sales;
    foundSaleInDB = await search_sale_byID(body.uid);
    if(foundSaleInDB):
        sales.update_one({ '_id': body.uid }, { "$set": { 'deleted': True } });
        return True;

    return JSONResponse(status_code=200, content={"Error": "Employee not found in DB inserted"})

# Helper functions
async def search_sale_byID(uid) :
    sales = mongo.sales;
    output = False;
    for q in sales.find({ '_id': uid }):
        output = True;

    return output;

