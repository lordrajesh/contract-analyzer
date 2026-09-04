from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import shutil

sys.path.append(os.path.dirname(__file__))

from parser import extract_text
from analyzer import analyze_contract

app = FastAPI(title="Contract Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def health_check():
    return {"status": "Contract Analyzer running"}


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    role: str = Form(...)
):
    """Upload contract + role → get risk analysis"""
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Extract text
    text = extract_text(file_path)
    if not text:
        return {"error": "Could not extract text from document"}

    # Analyze
    result = analyze_contract(text, role)
    return result