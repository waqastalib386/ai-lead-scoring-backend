
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
import os

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

app = FastAPI()
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def calculate_score(age, income, pages_visited):
    score = 0
    if 25 <= age <= 45:
        score += 20
    if income >= 80000:
        score += 30
    elif income >= 50000:
        score += 15
    if pages_visited >= 6:
        score += 30
    elif pages_visited >= 3:
        score += 15
    category = "Hot" if score >= 70 else "Warm" if score >= 40 else "Cold"
    return score, category

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/leads")
def get_leads():
    res = supabase.table("leads").select("*").order("created_at", desc=True).execute()
    return res.data

@app.post("/lead")
def create_lead(
    data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        age = int(data["age"])
        income = int(data["income"])
        pages = int(data["pages_visited"])
        time_spent = int(data["time_spent"])
        score, category = calculate_score(age, income, pages)
        res = supabase.table("leads").insert({
            "age": age,
            "income": income,
            "source": data["source"],
            "pages_visited": pages,
            "time_spent": time_spent,
            "score": score,
            "category": category,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
def login(data: dict):
    res = supabase.auth.sign_in_with_password({
        "email": data["email"],
        "password": data["password"]
    })
    return {
        "access_token": res.session.access_token,
        "token_type": "bearer"
    }

# NEW SIGNUP ENDPOINT - ADD THIS
@app.post("/signup")
def signup(data: dict):
    try:
        res = supabase.auth.sign_up({
            "email": data["email"],
            "password": data["password"]
        })
        
        if res.user:
            return {
                "status": "success",
                "message": "User created successfully!",
                "user_id": res.user.id
            }
        else:
            raise HTTPException(status_code=400, detail="Signup failed")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
