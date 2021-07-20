from os import error
from pydantic import BaseModel
from typing import Optional
from pydantic.main import BaseConfig
from bson.objectid import ObjectId
from pydantic.fields import Field
from datetime import datetime

class MongoModel(BaseModel):
    class Config(BaseConfig):
        json_encoders = {
            ObjectId: lambda oid: str(oid),
        }

class AuthModel(MongoModel):
    user: str = Field()
    password: str = Field()

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

class Employee(MongoModel):
    uid: Optional[OID]
    name: str = Field()
    user: str = Field()
    password: str = Field()
    deleted: Optional[bool]
    lastlogin: Optional[datetime]

# body class
class EmployeeBody(MongoModel):
    uid: Optional[OID]
    showDeleted: Optional[bool]