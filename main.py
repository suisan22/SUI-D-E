from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from forensics import detect_web_images
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

# 1. Define a Request Model (Best Practice)
class ScanRequest(BaseModel):
    url: str

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "success", "message": "SUI-D-E API is online!"}

@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    content = await file.read()
    return detect_web_images(content)

# 2. Use the Request Model in your scan route
@app.post("/scan")
async def scan(request: ScanRequest):
    target_url = request.url
    
    try:
        response = requests.get(target_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()[:2000]

        # Use valid model name
        model = genai.GenerativeModel("gemini-1.5-flash") 
        prompt = f"Analyze this content for malicious intent. Return ONLY JSON format {{\"isIllegal\": true/false, \"reason\": \"explanation\"}}. Content: {page_text}"
        
        ai_response = model.generate_content(prompt)
        
        raw_text = ai_response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(raw_text)
        
    except Exception as e:
        return {"isIllegal": False, "reason": f"Scan failed: {str(e)}"}
