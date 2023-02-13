from fastapi import FastAPI, Request
from bson import ObjectId
import motor.motor_asyncio
import pydantic
import os
from pydantic import BaseModel, Field, EmailStr
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Body, Request, HTTPException, status
from fastapi.responses import Response, JSONResponse
from datetime import datetime
from typing import Optional, List

app = FastAPI()

origins = [
    "http://localhost:8000",
    "https://ecse3038-lab3-tester.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://tiamia:Ve6yYRwlN4WliSOd@cluster0.kuljwrw.mongodb.net/?retryWrites=true&w=majority", tls=True, tlsAllowInvalidCertificates=True)
db = client.water_tank

pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str

@app.get("/profile")
async def get_profile():
    profile = await db["Data"].find_one()
    return profile

@app.post("/profile", status_code=201)
async def create_profile(request: Request):
    profile_object = await request.json()
    profile_object["last_updated"]=datetime.now()

    new_profile = await db["Data"].insert_one(profile_object)
    created_profile = await db["Data"].find_one({"_id": new_profile.inserted_id})
    return created_profile

@app.get("/data")
async def get_all_data():
    datas = await db["Waterdata"].find().to_list(999)
    return datas

@app.post("/data", status_code=201)
async def create_data(request: Request):
    data_object = await request.json()

    new_data = await db["Waterdata"].insert_one(data_object)
    created_data = await db["Waterdata"].find_one({"_id": new_data.inserted_id})
    return created_data

@app.patch("/data/{id}")
async def update_data(id: str, request: Request):
    info = await request.json()         
    updated_data = await db["Waterdata"].update_one({"_id": ObjectId(id)}, {"$set": info})
    result = await db["Waterdata"].find_one({"_id":id})
    return result

@app.delete("/data/{id}", status_code=204)        
async def delete_data(id: str):
    to_delete =  await db["Waterdata"].find_one_and_delete({"_id": ObjectId(id)}) 

    if not to_delete:
        raise HTTPException(status_code=404, detail="Not Found")