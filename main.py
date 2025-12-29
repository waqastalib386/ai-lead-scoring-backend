
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("❌ SUPABASE ENV NOT LOADED")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Lead(BaseModel):
    age: int
    income: int
    source: str
    time_spent: int
    pages_visited: int

@app.post("/predict")
def predict(data: Lead):
    score = 0
    if data.income > 80000: score += 40
    if data.time_spent > 300: score += 30
    if data.pages_visited > 5: score += 30

    category = "Cold"
    if score >= 80: category = "Hot Lead"
    elif score >= 50: category = "Warm"

    res = supabase.table("leads").insert({
        "age": data.age,
        "income": data.income,
        "source": data.source,
        "time_spent": data.time_spent,
        "pages_visited": data.pages_visited,
        "score": score
    }).execute()

    if res.data is None:
        raise Exception(f"❌ SUPABASE INSERT FAILED: {res}")

    return {
        "score": score,
        "category": category
    }

@app.get("/leads")
def leads():
    return supabase.table("leads").select("*").execute().data