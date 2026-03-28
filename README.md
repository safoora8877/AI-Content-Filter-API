# 🛡️ AI content filter

It is a real-time AI-powered content filtering system that analyzes web queries and URLs to detect adult or unsafe content. It is designed to integrate with mobile applications to enable secure and intelligent browsing experiences.

---

## 🚀 Features

- 🔍 Real-time content classification (Safe / Adult)
- 🤖 AI-powered decision making using LLM
- 📊 Confidence score and reasoning output
- ⚡ FastAPI backend for high performance
- 📱 Designed for Android VPN-based filtering apps
- 🔒 Enhances safe browsing and parental control systems

---

## 🧠 How It Works

1. User sends text or URL to the API
2. The backend processes the request using AI
3. The system classifies content into categories:
   - Safe
   - Adult
4. Returns:
   - Decision
   - Confidence score
   - Reason
   - Category

---

## 🏗️ Tech Stack

- **Backend:** FastAPI
- **Language:** Python
- **AI Model:** LLM (via Groq API)
- **API Communication:** REST API (JSON)

---

## 📡 API Endpoint

### `POST /filter`

#### Request Body:
```json
{
  "text": "your input text or URL"
}
