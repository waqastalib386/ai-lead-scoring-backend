
from fastapi import APIRouter, Depends
from models import LeadCreate
from auth import get_current_user

router = APIRouter(prefix="/leads", tags=["Leads"])

fake_db = []

@router.post("/")
def create_lead(lead: LeadCreate, user=Depends(get_current_user)):
    data = lead.dict()
    data["id"] = len(fake_db) + 1
    fake_db.append(data)
    return {"message": "Lead saved", "lead": data}

@router.get("/")
def get_leads(user=Depends(get_current_user)):
    return fake_db

@router.post("/leads/")
def create_lead(lead: LeadCreate, user=Depends(get_current_user)):
    return lead