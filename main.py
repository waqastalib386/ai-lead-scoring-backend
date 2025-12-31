
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)
from fastapi import Header, HTTPException, Depends
import jwt

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    
from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/lead")
def add_lead(data: dict, user_id: str = Depends(get_current_user)):

    score = data["time_spent"] + data["pages_visited"] * 10

    if score >= 80:
        category = "Hot Lead"
    elif score >= 50:
        category = "Warm Lead"
    else:
        category = "Cold Lead"

    supabase.table("leads").insert({
        "user_id": user_id,
        "time_spent": data["time_spent"],
        "pages_visited": data["pages_visited"],
        "score": score,
        "category": category
    }).execute()

    return {
        "message": "Lead saved successfully",
        "score": score,
        "category": category
    }

@app.get("/leads")
def get_leads(user_id: str = Depends(get_current_user)):
    response = (
        supabase
        .table("leads")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    return response.data