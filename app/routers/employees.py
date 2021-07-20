from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from pymongo import MongoClient;
from starlette.responses import JSONResponse;
from auth.auth import AuthHandler;
from models.employee import *;

router = APIRouter();

auth_handler = AuthHandler();

client = MongoClient('mongodb://localhost:27017/');
mongo = client['petstore'];

# Login
@router.post('/employees/authenticated')
async def login(authInfo : AuthModel):
    # Check if user is in DB:
    if( await search_employee_byUSER(authInfo.user)) :
        # get User password and compare:
        password = await get_user_passsword(authInfo.user);
        if ( not auth_handler.verify_password(authInfo.password, password)) :
            raise HTTPException(status_code=401, detail='Invalid Username and/or password');
        
        token = auth_handler.encode_token(authInfo.user);
        return { 'token' : token }

    raise HTTPException(status_code=401, detail='User not found');

# Get all employees
@router.get('/employees')
async def get_all_employees(body : EmployeeBody, token = Depends(auth_handler.auth_wrapper)):
    employees = mongo.employees;
    output = [];
    query = { '$or' : [ {'deleted': { '$exists': False}} , { 'deleted': None }] } if not body.showDeleted else {};
    for q in employees.find(query):
        id = str(q['_id']);
        output.append({ 'id': id ,'name': q['name'], 'username': q['user'], 'password': q['password'] });

    return (output);

# Get an specific employee
@router.get('/employees/{uid}')
async def get_employee(uid: OID, token = Depends(auth_handler.auth_wrapper)):
    employees = mongo.employees;
    output = [];
    for q in employees.find({ '_id': uid }):
        id = str(q['_id']);
        output.append({ 'id': id ,'name': q['name'], 'username': q['user'], 'password': q['password'] });

    return (output);

# Post an employee
@router.post('/employees/signup', response_model=Employee)
async def post_employee(employeeInfo : Employee, token = Depends(auth_handler.auth_wrapper)):
    employees = mongo.employees;
    foundEmployeeInDB = await search_employee_byUSER(employeeInfo.user);
    if(not foundEmployeeInDB):
        employees.insert_one(employeeInfo.__dict__)
        return employeeInfo;

    return JSONResponse(status_code=200, content={"Error": "Employee already inserted"})

# Update an specific employee
@router.patch('/employees', response_model=Employee)
async def update_employee(employeeInfo : Employee, token = Depends(auth_handler.auth_wrapper)):
    employees = mongo.employees;
    foundEmployeeInDB = await search_employee_byID(employeeInfo.uid);
    if(foundEmployeeInDB):
        employees.update_one({ '_id': employeeInfo.uid }, { "$set" : employeeInfo.__dict__})
        return employeeInfo;

    return JSONResponse(status_code=200, content={"Error": "Employee not found in DB inserted"})

# Remove an specific employee
@router.delete('/employees')
async def delete_employee(body: EmployeeBody, token = Depends(auth_handler.auth_wrapper)):
    employees = mongo.employees;
    foundEmployeeInDB = await search_employee_byID(body.uid);
    if(foundEmployeeInDB):
        employees.update_one({ '_id': body.uid }, { "$set": { 'deleted': True } })
        return True;

    return JSONResponse(status_code=200, content={"Error": "Employee not found in DB inserted"})

# Helper functions
async def search_employee_byUSER(user) :
    employees = mongo.employees;
    output = False;
    for q in employees.find({ 'user': user }):
        output = True;

    return output;

async def search_employee_byID(uid) :
    employees = mongo.employees;
    output = False;
    for q in employees.find({ '_id': uid }):
        output = True;

    return output;

async def get_user_passsword(user) :
    employees = mongo.employees;
    password = '';
    for q in employees.find({ 'user': user }):
        return q['password'];

    return password;

