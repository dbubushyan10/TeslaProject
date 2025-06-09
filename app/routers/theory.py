from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.utils import templates

router = APIRouter(prefix="/theory", tags=["theory"])

@router.get("/")
async def theory_home(request: Request):
    return templates.TemplateResponse("theory.html", {"request": request})

@router.get("/rectifier")
async def rectifier(request: Request):
    return templates.TemplateResponse("theory/theory_rectifier.html", {"request": request})

@router.get("/transistor_params")
async def transistor_params(request: Request):
    return templates.TemplateResponse("theory/theory_transistor_params.html", {"request": request})

@router.get("/amplifier_stage")
async def amplifier_stage(request: Request):
    return templates.TemplateResponse("theory/theory_amplifier_stage.html", {"request": request})

@router.get("/opamp_circuits")
async def opamp_circuits(request: Request):
    return templates.TemplateResponse("theory/theory_opamp_circuits.html", {"request": request})

@router.get("/transfer_function")
async def transfer_function(request: Request):
    return templates.TemplateResponse("theory/theory_transfer_function.html", {"request": request})
