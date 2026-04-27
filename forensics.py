import requests
import os
from requests.auth import HTTPBasicAuth

def detect_web_images(file_content):
    api_key = os.getenv("IMAGGA_API_KEY")
    api_secret = os.getenv("IMAGGA_API_SECRET")
    
    upload_url = "https://api.imagga.com/v2/uploads"
    # Imagga needs the file as 'image'
    files = {'image': file_content}
    response = requests.post(upload_url, auth=HTTPBasicAuth(api_key, api_secret), files=files)
    
    data = response.json()
    print("Imagga Response:", data) # CHECK THIS IN TERMINAL

    if 'result' in data and 'upload_id' in data['result']:
        upload_id = data['result']['upload_id']
        tagging_url = f"https://api.imagga.com/v2/tags?image_upload_id={upload_id}"
        tag_response = requests.get(tagging_url, auth=HTTPBasicAuth(api_key, api_secret))
        tag_data = tag_response.json()
        
        if 'result' in tag_data:
            tags = tag_data['result']['tags']
            tag_names = [t['tag']['en'] for t in tags[:5]]
            return {"urls": tag_names, "found": True}
            
    return {"found": False, "error": "Could not identify image"}