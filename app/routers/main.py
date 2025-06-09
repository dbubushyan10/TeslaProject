# app/routers/main.py
from fastapi import APIRouter, Request
from app.utils import templates

router = APIRouter()

@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
