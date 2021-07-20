from fastapi import FastAPI;
from routers import employees, clients, dogs, products, sales;
from pymongo import MongoClient;

app = FastAPI();

app.include_router(employees.router);
app.include_router(clients.router);
app.include_router(dogs.router);
app.include_router(products.router);
app.include_router(sales.router);

client = MongoClient('mongodb://localhost:27017/');
mongo = client['petstore']

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

def main() :
    return app;