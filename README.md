# AutoStream Conversational AI Agent

A LangGraph-powered AI sales agent for AutoStream — a fictional SaaS video editing platform.

---

## How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/autostream-agent.git
cd autostream-agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your API key
```bash
export GOOGLE_API_KEY=your_gemini_api_key_here
```

### 4. Run the agent
```bash
python agent.py
```

---

## Architecture Explanation (~200 words)

This agent is built using **LangGraph**, a stateful graph framework built on top of LangChain. LangGraph was chosen because it allows explicit control over conversation flow using a directed graph of nodes, making it easy to manage multi-turn state, conditional routing, and tool execution in a clean and inspectable way — unlike a simple chain or a black-box agent loop.

**State Management:** The entire conversation state is stored in a single `AgentState` TypedDict that persists across all turns. It tracks the conversation history (as a list of LangChain messages), the detected intent, the lead collection progress (name, email, platform), and what information the agent is currently awaiting. This state is passed through the graph on every turn and updated in-place, giving the agent full memory across 5–6+ conversation turns without any external database.

**Graph Flow:** Each user message triggers a two-node pipeline: `detect_intent` (classifies the user's goal) → `generate_response` (uses RAG retrieval or LLM to respond, or collects lead data). The graph uses conditional edges to decide whether to end the session (after lead capture) or return control to the user.

---

## WhatsApp Deployment via Webhooks

To deploy this agent on WhatsApp:

1. **Use Twilio or Meta's WhatsApp Business API** to get a WhatsApp-enabled phone number.
2. **Create a Flask or FastAPI webhook endpoint** (e.g., `POST /webhook`) that receives incoming WhatsApp messages as JSON payloads.
3. **Map the sender's phone number to a session** — store each user's `AgentState` in a dictionary or Redis keyed by phone number, so memory persists across messages.
4. **Run the LangGraph agent** with the incoming message appended to that session's state, then **send the agent's reply back** via Twilio's `client.messages.create()` or Meta's Graph API.
5. **Host the webhook** on a public server (e.g., Railway, Render, or AWS) with HTTPS, and register the URL in the Twilio/Meta dashboard.

This architecture means each WhatsApp user gets their own isolated, persistent state — making the multi-turn lead capture flow work seamlessly over WhatsApp.
