from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
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
gemini_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_key)

app = FastAPI()
@app.get("/")
async def root():
    return {"status": "success", "message": "SUI-D-E API is online and ready for scans!"}

# Enable CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for demo purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    content = await file.read()
    return detect_web_images(content)

@app.post("/scan")
async def scan(data: dict):
    target_url = data.get("url")
    if not target_url:
        return {"isIllegal": False, "reason": "No URL provided"}

    try:
        # Fetch content
        response = requests.get(target_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()[:2000]

        # AI Analysis
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"Analyze this content for copyright infringement, piracy, or malicious intent. Return ONLY raw JSON in this format: {{\"isIllegal\": true/false, \"reason\": \"explanation\"}}. Content: {page_text}"
        
        ai_response = model.generate_content(prompt)
        
        # Clean up response to ensure it's parseable
        raw_text = ai_response.text.replace("```json", "").replace("```", "").strip()
        result_dict = json.loads(raw_text)
        
        return result_dict
        
    except json.JSONDecodeError:
        return {"isIllegal": False, "reason": "AI returned invalid format."}
    except Exception as e:
        # Return a structured error so the frontend doesn't crash
        return {"isIllegal": False, "reason": f"Scan failed: {str(e)}"}
