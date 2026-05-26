"""

This module defines the API routes for the "entries" resource. It uses FastAPI's APIRouter to create a router that can be included in the main application. The router is tagged with "entries" for better organization in the API documentation. The example route defined here returns a simple message when accessed via a GET request to "/entries".

"""
from fastapi import APIRouter


router = APIRouter(tags=["entries"])
@router.get(
    "/entries",
    summary="ดึงรายการ Entries",
    description="API สำหรับดึงข้อมูล Entries ทั้งหมดจากระบบ",
    response_description="รายการ Entries ทั้งหมด"
)
async def read_entries():
    return {"message": "Hello, Entries!"}