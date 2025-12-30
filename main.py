
from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client
import os

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class Lead(BaseModel):
    age: int
    income: int
    source: str
    time_spent: int
    pages_visited: int

def calculate_score(data: Lead):
    score = 0
    if data.income > 80000:
        score += 40
    if data.time_spent > 300:
        score += 30
    if data.pages_visited >= 7:
        score += 30
    return min(score, 100)

def get_category(score: int):
    if score >= 80:
        return "Hot Lead"
    elif score >= 50:
        return "Warm Lead"
    else:
        return "Cold Lead"

@app.post("/predict")
def predict(lead: Lead):
    score = calculate_score(lead)
    category = get_category(score)

    supabase.table("leads").insert({
        "age": lead.age,
        "income": lead.income,
        "source": lead.source,
        "time_spent": lead.time_spent,
        "pages_visited": lead.pages_visited,
        "score": score,
        "category": category
    }).execute()

    return {
        "score": score,
        "lead_category": category
    }