
from fastapi import FastAPI
from pydantic import BaseModel
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

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

    score = lead.time_spent + lead.pages_visited * 10

    if score >= 80:
        category = "Hot Lead"
    elif score >= 50:
        category = "Warm Lead"
    else:
        category = "Cold Lead"

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