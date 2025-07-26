from fastapi import APIRouter , Depends

base_router = APIRouter(tags=['api_v1'])
@base_router.get("/")
def Welcome():
    return {"Name" : "mazen",
            "Version":"1.1.1"}