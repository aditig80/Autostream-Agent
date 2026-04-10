# 🎬 AutoStream Conversational AI Agent

A Conversational AI Sales Agent for **AutoStream** — a SaaS platform for automated video editing. Built with **LangGraph**, **LangChain**, and **GPT-4o-mini**.

---

## 🚀 How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/autostream-agent.git
cd autostream-agent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Your OpenAI API Key

**Windows CMD:**
```cmd
set OPENAI_API_KEY=your_openai_api_key_here
```
**Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY="your_openai_api_key_here"
```

### 4. Run the Agent
```bash
python agent.py
```

---

## 🏗️ Architecture Explanation

This agent is built using **LangGraph**, a stateful graph framework on top of LangChain. LangGraph was chosen because it gives explicit control over the conversation flow through a directed graph of nodes — making it easy to manage multi-turn state, intent routing, and tool execution cleanly and predictably.

**State Management:** All conversation data is stored in a single `AgentState` TypedDict that persists across turns. It tracks the full message history, detected intent, lead collection progress (name, email, platform), and what info the agent is currently awaiting. This state is passed through the LangGraph on every turn and updated in place — giving the agent complete memory across 5–6+ turns with no external database needed.

**Graph Flow:** Each user message goes through two nodes — `detect_intent` (classifies the message) → `generate_response` (uses RAG or collects lead data). The `mock_lead_capture()` tool is only fired after all three lead details are collected.

---

## 📱 WhatsApp Deployment via Webhooks

1. **Get a WhatsApp number** via Twilio or Meta's WhatsApp Business API.
2. **Build a FastAPI webhook** (`POST /webhook`) that receives incoming messages and passes them to the LangGraph agent.
3. **Store each user's `AgentState`** in a dictionary or Redis keyed by their phone number, so memory persists between messages.
4. **Send the agent's reply back** via Twilio's or Meta's messaging API.
5. **Host publicly** on Railway or Render and register the URL as your webhook in the Twilio/Meta dashboard.

This gives every WhatsApp user their own isolated, persistent session — making the full multi-turn lead capture flow work seamlessly over WhatsApp.

---

## 📁 Project Structure

```
autostream-agent/
├── agent.py             # Agent logic (LangGraph + RAG + Intent + Tool)
├── knowledge_base.json  # Local knowledge base (pricing, policies)
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## 📋 Requirements

```
langgraph>=0.1.0
langchain>=0.2.0
langchain-core>=0.2.0
langchain-openai>=0.1.0
openai>=1.0.0
```
