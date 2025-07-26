from fastapi import FastAPI
from routes import base_router, StreamReadingRoute
from motor.motor_asyncio import AsyncIOMotorClient
app = FastAPI()
from Helper import get_setting , Settings
@app.on_event("startup")
async def startup():
    env = get_setting()

    app.MongoConnection = AsyncIOMotorClient(env.CLIENT) ## to env
    app.db_client = app.MongoConnection[env.DB_NAME] ## add to env


app.include_router(base_router)
app.include_router(StreamReadingRoute)
@app.on_event("shutdown")
async def shutdown():
    app.MongoConnection.close()