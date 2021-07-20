from pydantic import BaseModel;
from typing import Optional;
from pydantic.fields import Field;
from pydantic.main import BaseConfig;
from os import error;
from bson.objectid import ObjectId;

class MongoModel(BaseModel):
    class Config(BaseConfig):
        json_encoders = {
            ObjectId: lambda oid: str(oid),
        }

class OID(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            return ObjectId(str(v))
        except error:
            raise ValueError("Not a valid ObjectId")

class Product(MongoModel):
    uid: Optional[OID]
    name: str = Field()
    price: float = Field()
    description: str = Field()
    deleted: Optional[bool]

class ProductBody(MongoModel):
    uid: Optional[OID]
    showDeleted: Optional[bool]
