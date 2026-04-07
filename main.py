
import os
import json
import re
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from groq import Groq

load_dotenv()

def load_policy():
    with open("filtering-policy.md", "r", encoding="utf-8") as f:
        return f.read()
SYSTEM_PROMPT = load_policy()

app = FastAPI(title="SafeBrowse AI Content Filter")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class FilterRequest(BaseModel):
    query: str

class FilterResponse(BaseModel):
    decision: str
    confidence: int
    reason: str
    category: str
    alert_message: str = "This content is not suitable for children."

# Welcome Page
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head><title>SafeBrowse AI Filter</title>
        <style>body{font-family:Arial;background:#0f172a;color:white;text-align:center;padding:60px;}
        h1{color:#22c55e;} .card{background:#1e2937;padding:40px;border-radius:20px;max-width:700px;margin:40px auto;}</style>
        </head>
        <body>
            <h1>✅ SafeBrowse AI Content Filter (Groq)</h1>
            <div class="card">
                <p>Backend is running successfully with Groq!</p>
                <p><a href="/docs" style="color:#60a5fa;">Test the filter here → /docs</a></p>
            </div>
        </body>
    </html>
    """

@app.post("/filter", response_model=FilterResponse)
async def filter_content(request: FilterRequest):
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",   # best for strict JSON
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this query: {request.query}"}
            ],
            temperature=0.1,                    # low temperature = more consistent
            max_tokens=300,
            response_format={"type": "json_object"}   # forces valid JSON
        )

        final_text = response.choices[0].message.content.strip()

        # Extract JSON safely
        json_match = re.search(r'\{.*\}', final_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
        else:
            result = {}

        decision = str(result.get("decision", "allow")).lower()
        confidence = int(result.get("confidence", 70))
        reason = result.get("reason", "Content analyzed")
        category = result.get("category", "other")


        query_lower = request.query.lower()
    
    # Start with your backend decision (from API or other logic)
    # Assume `decision`, `confidence`, `reason`, `category` are already set

    # ⭐ Extra safety fallback: harmful keywords
    harmful_keywords = ["porn", "sex", "xxx", "nude", "fuck", "murder", "assault",
    "abuse", "rape", "gun", "weapon", "stab", "cocaine", "heroin", "meth", "lsd", "weed"]
    adult_keywords = ["porn", "sex", "xxx", "nude", "erotic", "fetish", "boobs", "cock", "dick", "pussy", "fuck", "cum"]
    violence_keywords = ["murder"]

    if any(word in query_lower for word in harmful_keywords) and decision != "block":
        decision = "block"
        confidence = 95
        reason = "Harmful or dangerous keyword detected"
        if any(word in query_lower for word in adult_keywords):
            category = "adult"
        elif any(word in query_lower for word in violence_keywords):
            category = "violence"
        else:
            category = "unknown"

    return FilterResponse(
        decision=decision,
        confidence=confidence,
        reason=reason,
        category=category,
        alert_message="This content is not suitable for children." if decision == "block" else ""
    )

except Exception as e:
    print("Error:", str(e))
    # Strong fallback: block if any dangerous keywords are present
    query_lower = request.query.lower()
    if any(word in query_lower for word in harmful_keywords):
        category = "adult" if any(word in query_lower for word in adult_keywords) else "violence"
        return FilterResponse(
            decision="block",
            confidence=90,
            reason="Dangerous or inappropriate content detected",
            category=category,
            alert_message="This content is not suitable for children."
        )
    # If all else fails
    return FilterResponse(
        decision="allow",
        confidence=50,
        reason="Processing error - treated as safe",
        category="safe",
        alert_message=""
    )

       
    
if __name__ == "__main__":
    import uvicorn
