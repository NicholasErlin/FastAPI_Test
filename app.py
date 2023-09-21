from datetime import datetime
import os
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from typing import Optional, List
import motor.motor_asyncio

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://admin:admin@clustertest.33x3iom.mongodb.net/test?retryWrites=true&w=majority")
db = client.core2data


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class AirDataModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    eco2: int = Field(...)
    h2: int = Field(...)
    ethanol: int = Field(...)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "eco2": 2,
                "h2": 3,
                "ethanol": 7
            }
        }


class UpdateAirDataModel(BaseModel):
    eco2: Optional[int]
    h2: Optional[int]
    ethanol: Optional[int]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "eco2": 2,
                "h2": 3,
                "ethanol": 7
            }
        }


@app.post("/", response_description="Add new Air Data Value", response_model=AirDataModel)
async def create_airdata(airData: AirDataModel = Body(...)):
    airData = jsonable_encoder(airData)
    new_airData = await db["airData"].insert_one(airData)
    created_airData = await db["airData"].find_one({"_id": new_airData.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_airData)


@app.get(
    "/", response_description="List all Air Data Values", response_model=List[AirDataModel]
)
async def list_airData():
    airData = await db["airData"].find().to_list(1000)
    return airData


@app.get(
    "/{id}", response_description="Get a single Air Data by Id", response_model=AirDataModel
)
async def show_airData(id: str):
    if (airData := await db["airData"].find_one({"_id": id})) is not None:
        return airData

    raise HTTPException(status_code=404, detail=f"Air Data {id} not found")


@app.put("/{id}", response_description="Update an Air Data Value", response_model=AirDataModel)
async def update_airData(id: str, airData: UpdateAirDataModel = Body(...)):
    airData = {k: v for k, v in airData.dict().items() if v is not None}

    if len(airData) >= 1:
        update_result = await db["airData"].update_one({"_id": id}, {"$set": airData})

        if update_result.modified_count == 1:
            if (
                updated_airData := await db["airData"].find_one({"_id": id})
            ) is not None:
                return updated_airData

    if (existing_airData := await db["airData"].find_one({"_id": id})) is not None:
        return existing_airData

    raise HTTPException(status_code=404, detail=f"Air Data Value {id} not found")


@app.delete("/{id}", response_description="Delete an Air Data Value")
async def delete_airData(id: str):
    delete_result = await db["airData"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Air Data Value {id} not found")
