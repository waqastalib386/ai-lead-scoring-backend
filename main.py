
import os
import jwt
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client

# -----------------------------
# ENV VARIABLES (Render only)
# -----------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY or not SUPABASE_JWT_SECRET:
    raise Exception("Missing required Supabase environment variables")

# -----------------------------
# Supabase Client (SAFE INIT)
# -----------------------------
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

supabase = get_supabase()

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Auth: Get Current User
# -----------------------------
def get_current_user(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        return payload["sub"]  # user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# -----------------------------
# API: Add Lead
# -----------------------------
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

# -----------------------------
# API: Get Leads (User-wise)
# -----------------------------
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