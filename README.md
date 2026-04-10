# 🎬 AutoStream Conversational AI Agent

A production-ready Conversational AI Sales Agent built for **AutoStream** — a fictional SaaS platform providing automated video editing tools for content creators. Built using **LangGraph**, **LangChain**, and **GPT-4o-mini**.

---

## 📌 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [How to Run Locally](#how-to-run-locally)
- [Example Conversation](#example-conversation)
- [Architecture Explanation](#architecture-explanation)
- [WhatsApp Deployment via Webhooks](#whatsapp-deployment-via-webhooks)

---

## 📖 Project Overview

AutoStream AI Agent is a multi-turn conversational agent that acts as an intelligent sales assistant. It can:

- Greet users and answer general questions
- Retrieve accurate pricing and policy information from a local knowledge base (RAG)
- Detect when a user is ready to sign up (high-intent detection)
- Collect user details (name, email, platform) in a guided flow
- Trigger a lead capture tool once all details are collected

The agent maintains memory across the entire conversation, meaning it remembers what was said earlier and responds contextually — just like a real sales representative.

---

## ✅ Features

| Feature | Description |
|---|---|
| 🧠 Intent Detection | Classifies every message as greeting, inquiry, or high-intent |
| 📚 RAG Knowledge Base | Answers questions using a local JSON knowledge base |
| 🔄 State Management | Full conversation memory across 5–6+ turns using LangGraph |
| 🛠️ Tool Execution | Fires `mock_lead_capture()` only after all 3 details are collected |
| 💬 Natural Conversation | Friendly, guided multi-turn dialogue flow |

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.9+ |
| Agent Framework | LangGraph (LangChain) |
| LLM | GPT-4o-mini (OpenAI) |
| Knowledge Base | Local JSON file (RAG) |
| State Management | LangGraph `StateGraph` with `TypedDict` |

---

## 📁 Project Structure

```
autostream-agent/
│
├── agent.py               # Main agent logic (LangGraph + RAG + Intent + Tool)
├── knowledge_base.json    # Local knowledge base (pricing, policies, company info)
├── requirements.txt       # All Python dependencies
└── README.md              # Project documentation (this file)
```

---

## 🚀 How to Run Locally

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/autostream-agent.git
cd autostream-agent
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Your OpenAI API Key

**Windows CMD:**
```cmd
set OPENAI_API_KEY=your_openai_api_key_here
```

**Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY="your_openai_api_key_here"
```

**Mac / Linux:**
```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

### Step 4: Run the Agent

```bash
python agent.py
```

### Step 5: Talk to the Agent

Type messages in the terminal. Try this conversation flow:

```
You: Hi
You: Tell me about your pricing
You: What is your refund policy?
You: I want to try the Pro plan for my YouTube channel
You: John Doe
You: john@example.com
You: YouTube
```

---

## 💬 Example Conversation

```
🎬 Welcome to AutoStream AI Agent
Type 'quit' or 'exit' to stop.
--------------------------------------------------

You: Hi

Agent: Hey there! 👋 Welcome to AutoStream — your automated video editing co-pilot!
I can help you with Pricing & Plans, Features, Policies, and Getting you signed up!

--------------------------------------------------

You: Tell me about your pricing

Agent: AutoStream offers two plans:
- Basic Plan: $29/month — 10 videos/month, 720p resolution
- Pro Plan: $79/month — Unlimited videos, 4K resolution, AI captions & 24/7 support

--------------------------------------------------

You: What is the refund policy?

Agent: AutoStream does not offer refunds after 7 days of purchase.
24/7 support is available exclusively on the Pro plan.

--------------------------------------------------

You: I want to try the Pro plan for my YouTube channel

Agent: That's awesome! 🙌 Let me get you set up.
First — what's your full name?

--------------------------------------------------

You: John Doe

Agent: Got it! Now, could you please share your email address?

--------------------------------------------------

You: john@example.com

Agent: Almost there! Which creator platform do you primarily use?
(e.g., YouTube, Instagram, TikTok, Twitch)

--------------------------------------------------

You: YouTube

==================================================
✅ Lead captured successfully: John Doe, john@example.com, YouTube
==================================================

Agent: 🎉 You're all set, John Doe!
We've captured your details and our team will reach out shortly.
Welcome to AutoStream Pro — let's create something amazing! 🚀
```

---

## 🏗️ Architecture Explanation

### Why LangGraph?

LangGraph was chosen over a simple LangChain chain or basic AutoGen setup because it provides **explicit, inspectable control over conversation flow** using a directed state graph. Each node in the graph represents a discrete step — intent detection and response generation — and edges define how the agent transitions between them. This makes the agent's behavior predictable, debuggable, and easy to extend.

Unlike a black-box agent loop, LangGraph lets us define exactly **when** to call the LLM, **when** to fire tools, and **when** to end the conversation — all based on structured state. This is critical for a lead capture flow where premature tool execution must be prevented.

### How State is Managed

The entire conversation is stored in a single `AgentState` TypedDict that persists across all turns. It tracks:

- `messages` — Full conversation history as LangChain message objects
- `intent` — The classified intent of the latest user message
- `awaiting` — Which piece of lead info the agent is currently waiting for
- `lead_name`, `lead_email`, `lead_platform` — Collected lead data
- `lead_captured` — Boolean flag to end the conversation after successful capture

This state is passed into the LangGraph on every turn and updated in place, giving the agent complete memory across 5–6+ conversation turns without any external database or vector store. The RAG layer retrieves relevant knowledge base content by matching keywords from the user's message against the local JSON file, and this content is injected into the LLM prompt dynamically.

### Graph Flow

```
User Message
     │
     ▼
[detect_intent]  ──►  classifies as: greeting / inquiry / high_intent
     │
     ▼
[generate_response]  ──►  RAG retrieval + LLM response OR lead collection step
     │
     ▼
  END (or next turn)
```

---

## 📱 WhatsApp Deployment via Webhooks

To deploy this AutoStream agent on WhatsApp, follow this architecture:

### Step 1: Set Up WhatsApp Business API
Use either **Twilio WhatsApp API** (easiest) or **Meta's official WhatsApp Business Cloud API** to get a WhatsApp-enabled phone number and credentials.

### Step 2: Build a Webhook Endpoint
Create a simple **FastAPI** or **Flask** server with a `POST /webhook` endpoint that receives incoming WhatsApp messages:

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    sender = data["From"]           # WhatsApp number of the user
    message = data["Body"]          # Text message they sent
    reply = run_agent(sender, message)   # Run your LangGraph agent
    send_whatsapp_reply(sender, reply)   # Send reply back via Twilio/Meta API
    return {"status": "ok"}
```

### Step 3: Persist State Per User
Since every WhatsApp message is a separate HTTP request, you must store each user's `AgentState` between messages. Use a dictionary (for development) or **Redis** (for production) keyed by the sender's phone number:

```python
user_sessions = {}   # { phone_number: AgentState }

def run_agent(phone_number, message):
    if phone_number not in user_sessions:
        user_sessions[phone_number] = create_fresh_state()
    state = user_sessions[phone_number]
    state["messages"].append(HumanMessage(content=message))
    state = app.invoke(state)
    return state["messages"][-1].content
```

### Step 4: Deploy Publicly
Host your webhook on a public HTTPS server such as:
- **Railway** (free tier available)
- **Render** (free tier available)
- **AWS EC2 / Lambda**

Then register your public URL in the Twilio dashboard or Meta Developer Console as the webhook URL.

### Step 5: Full Flow on WhatsApp

```
WhatsApp User sends message
        │
        ▼
Twilio / Meta API receives it
        │
        ▼
POST request sent to your webhook URL
        │
        ▼
FastAPI server receives message + looks up user session
        │
        ▼
LangGraph agent processes it with full memory
        │
        ▼
Reply sent back to user via WhatsApp
```

This architecture ensures every WhatsApp user gets their own **isolated, persistent conversation state**, making the full multi-turn lead capture flow work seamlessly over WhatsApp — exactly as it does in the terminal.

---

## 📋 Requirements

See `requirements.txt`:

```
langgraph>=0.1.0
langchain>=0.2.0
langchain-core>=0.2.0
langchain-openai>=0.1.0
openai>=1.0.0
```

---

## 👨‍💻 Author

Built as part of an AI Agent assignment demonstrating LangGraph-based conversational agents with RAG, intent detection, state management, and tool execution.
