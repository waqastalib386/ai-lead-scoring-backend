
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- INIT ----------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

# ---------- MODEL ----------
class LeadInput(BaseModel):
    age: int
    income: int
    source: str
    time_spent: int
    pages_visited: int

# ---------- SCORING ----------
def calculate_score(data: LeadInput):
    score = 0

    if data.age < 35:
        score += 20
    if data.income > 80000:
        score += 30
    if data.source.lower() in ["google", "linkedin"]:
        score += 20
    if data.time_spent > 300:
        score += 15
    if data.pages_visited > 5:
        score += 15

    if score >= 70:
        category = "Hot"
    elif score >= 40:
        category = "Warm"
    else:
        category = "Cold"

    return score, category

# ---------- POST: PREDICT + SAVE ----------
@app.post("/predict")
def predict_lead(data: LeadInput):
    score, category = calculate_score(data)

    lead = {
        "age": data.age,
        "income": data.income,
        "source": data.source,
        "time_spent": data.time_spent,
        "pages_visited": data.pages_visited,
        "score": score,
        "category": category,
        "created_at": datetime.utcnow().isoformat()
    }

    supabase.table("leads").insert(lead).execute()

    return {
        "score": score,
        "category": category
    }

# ---------- GET: READ LEADS ----------
@app.get("/leads")
def get_leads():
    response = supabase.table("leads").select("*").order("created_at", desc=True).execute()
    return response.data
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")