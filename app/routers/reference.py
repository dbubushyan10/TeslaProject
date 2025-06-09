from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from app.utils import templates
router = APIRouter()

@router.get("/reference", response_class=HTMLResponse)
async def reference_page(request: Request):
    return templates.TemplateResponse("reference.html", {"request": request})
