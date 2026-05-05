import random
import time
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import uvicorn

app = FastAPI()

# Stats Tracking
stats = {
    "total_requests": 0,
    "active_requests": 0,
    "start_time": time.time()
}

# LIST OF YOUR HUGGING FACE SPACE URLS
BACKEND_URLS = [
    'https://aixflymasterrouter-earn-desk-node-01.hf.space',
    'https://aixflymasterrouter-earn-desk-node-02.hf.space',
    'https://aixflymasterrouter-earn-desk-node-03.hf.space',
    'https://aixflymasterrouter-earn-desk-node-04.hf.space',
    'https://aixflymasterrouter-earn-desk-node-05.hf.space',
    'https://aixflymasterrouter-earn-desk-node-06.hf.space',
]


# YOUR HUGGING FACE TOKENS (For Multiple Accounts)
# Format: "username": "token"
TOKENS = {
    "aixflyMasterRouter": "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",
    "secondAccount": "PASTE_TOKEN_2_HERE",
    # Add more accounts and tokens as needed
}




# Round Robin Index
current_backend = 0

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    uptime = int(time.time() - stats["start_time"])
    hours, rem = divmod(uptime, 3600)
    minutes, seconds = divmod(rem, 60)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Whisper AI | Balancer Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg: #0a0a0c;
                --card-bg: rgba(255, 255, 255, 0.05);
                --primary: #00f2ff;
                --secondary: #7000ff;
                --text: #ffffff;
            }}
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Inter', sans-serif;
                background-color: var(--bg);
                color: var(--text);
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                overflow: hidden;
            }}
            .container {{
                width: 90%;
                max-width: 1000px;
                padding: 40px;
                background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%);
                border-radius: 30px;
                border: 1px solid rgba(255,255,255,0.1);
                backdrop-filter: blur(20px);
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                text-align: center;
            }}
            .header {{ margin-bottom: 50px; }}
            .header h1 {{ font-size: 2.5rem; font-weight: 800; letter-spacing: -1px; margin-bottom: 10px; }}
            .status-badge {{
                display: inline-flex;
                align-items: center;
                padding: 8px 16px;
                background: rgba(0, 242, 255, 0.1);
                border-radius: 100px;
                color: var(--primary);
                font-weight: 600;
                font-size: 0.9rem;
            }}
            .pulse {{
                width: 8px;
                height: 8px;
                background: var(--primary);
                border-radius: 50%;
                margin-right: 10px;
                box-shadow: 0 0 10px var(--primary);
                animation: pulse 1.5s infinite;
            }}
            @keyframes pulse {{
                0% {{ transform: scale(0.95); opacity: 0.5; }}
                50% {{ transform: scale(1.1); opacity: 1; }}
                100% {{ transform: scale(0.95); opacity: 0.5; }}
            }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
            }}
            .card {{
                padding: 30px;
                background: var(--card-bg);
                border-radius: 20px;
                border: 1px solid rgba(255,255,255,0.05);
                transition: transform 0.3s ease;
            }}
            .card:hover {{ transform: translateY(-5px); border-color: rgba(255,255,255,0.2); }}
            .card h3 {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 2px; color: rgba(255,255,255,0.5); margin-bottom: 15px; }}
            .card .val {{ font-size: 2rem; font-weight: 800; color: var(--text); }}
            .footer {{ margin-top: 50px; font-size: 0.8rem; color: rgba(255,255,255,0.3); }}
            #uptime {{ color: var(--secondary); }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>EARN DESK <span style="color: var(--primary)">AI</span></h1>
                <div class="status-badge"><div class="pulse"></div> SYSTEM ONLINE</div>
            </div>
            <div class="grid">
                <div class="card">
                    <h3>Total Requests</h3>
                    <div class="val">{stats["total_requests"]}</div>
                </div>
                <div class="card">
                    <h3>Active Agents</h3>
                    <div class="val" style="color: var(--primary)">{len(BACKEND_URLS)}</div>
                </div>
                <div class="card">
                    <h3>Current Load</h3>
                    <div class="val">{stats["active_requests"]}</div>
                </div>
                <div class="card">
                    <h3>Uptime</h3>
                    <div class="val" id="uptime">{hours:02d}:{minutes:02d}:{seconds:02d}</div>
                </div>
            </div>
            <div class="footer">
                &copy; 2026 EARN DESK AI Solver Network. All rights reserved.
            </div>
        </div>
        <script>
            // Simple refresh every 5 seconds
            setTimeout(() => window.location.reload(), 5000);
        </script>
    </body>
    </html>
    """
    return html_content


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

    # Update Stats
    stats["total_requests"] += 1
    stats["active_requests"] += 1

    try:
        # Read file data once to reuse in retries
        file_content = await file.read()
        
        # Try up to 3 different backends if one fails
        max_retries = min(len(BACKEND_URLS), 3)
        
        for attempt in range(max_retries):
            # Pick backend using Round Robin
            backend_url = BACKEND_URLS[current_backend]
            current_backend = (current_backend + 1) % len(BACKEND_URLS)
            
            print(f"Attempt {attempt + 1}: Forwarding to {backend_url}")

            try:
                files = {'file': (file.filename, file_content, file.content_type)}
                
                # Automatically pick the correct token based on the username in the URL
                target_token = None
                lower_url = backend_url.lower()
                for username, token in TOKENS.items():
                    u_lower = username.lower()
                    if f"/{u_lower}-" in lower_url or f"//{u_lower}-" in lower_url:
                        target_token = token
                        break
                
                if not target_token:
                    print(f"Error: No token found for {backend_url}")
                    continue # Try next backend


                
                # Headers for private space access
                headers = {"Authorization": f"Bearer {target_token}"}
                
                # Short timeout for "instant" feel - if one space is slow, move to next
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(f"{backend_url}/transcribe", files=files, headers=headers)

                    
                    if response.status_code == 200:

                        stats["active_requests"] -= 1
                        return response.json()
                    
                    print(f"Backend {backend_url} returned {response.status_code}. Retrying...")
            except Exception as e:
                print(f"Backend {backend_url} error: {str(e)}. Retrying...")
                continue
        
        stats["active_requests"] -= 1
        raise HTTPException(status_code=503, detail="All backends are busy or down. Please try again.")

    except Exception as e:
        stats["active_requests"] -= 1
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000) # Render default port
