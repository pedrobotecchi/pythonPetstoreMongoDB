from pydantic import BaseModel, errors;
from typing import Optional;
from pydantic.main import BaseConfig;
from pydantic.fields import Field;
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
        except errors:
            raise ValueError("Not a valid ObjectId")

class Dog(MongoModel):
    uid: Optional[OID]
    name: str = Field()
    breed: str = Field()
    furr: str = Field()
    size: str = Field()
    uid_client: str = Field()
    deleted: Optional[bool]

class DogBody(MongoModel):
    showDeleted: Optional[bool]
    uid: Optional[OID]