
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class Lead(BaseModel):
    age: int
    income: int
    source: str          # 🔥 FIXED
    time_spent: int
    pages_visited: int

def score_lead(data: Lead):
    score = 0
    if data.income > 80000:
        score += 40
    if data.time_spent > 250:
        score += 30
    if data.pages_visited > 5:
        score += 30
    category = "Hot Lead" if score >= 70 else "Cold Lead"
    return score, category

@app.post("/predict")
def predict(lead: Lead):
    score, category = score_lead(lead)

    supabase.table("leads").insert({
        "age": lead.age,
        "income": lead.income,
        "source": lead.source,        # 🔥 EXACT MATCH
        "time_spent": lead.time_spent,
        "pages_visited": lead.pages_visited,
        "score": score
    }).execute()

    return {
        "score": score,
        "lead_category": category
    }

@app.get("/leads")
def get_leads():
    res = supabase.table("leads").select("*").execute()
    return res.data