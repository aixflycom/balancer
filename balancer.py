import random
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
import httpx
import uvicorn

app = FastAPI()

# LIST OF YOUR HUGGING FACE SPACE URLS
# Example: ['https://user-space1.hf.space', 'https://user-space2.hf.space']
BACKEND_URLS = [
    'https://aixflyMasterRouter-solver.hf.space', # Your main space
    # Add more spaces here to increase capacity
]

# Round Robin Index
current_backend = 0

@app.get("/")
async def root():
    return {"status": "Whisper Load Balancer is running", "backends_active": len(BACKEND_URLS)}

@app.post("/transcribe")
async def balance_transcribe(file: UploadFile = File(...)):
    global current_backend
    
    if not BACKEND_URLS:
        raise HTTPException(status_code=500, detail="No backends configured")

    # Pick backend using Round Robin
    backend_url = BACKEND_URLS[current_backend]
    current_backend = (current_backend + 1) % len(BACKEND_URLS)
    
    print(f"Forwarding request to: {backend_url}")

    try:
        # Read file data
        file_content = await file.read()
        files = {'file': (file.filename, file_content, file.content_type)}

        # Forward request to Hugging Face Space
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{backend_url}/transcribe", files=files)
            
            if response.status_code != 200:
                print(f"Backend {backend_url} failed with status {response.status_code}")
                # Optional: Try another backend if this one fails
                return response.json(), response.status_code
            
            return response.json()

    except Exception as e:
        print(f"Error forwarding to backend: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000) # Render default port
