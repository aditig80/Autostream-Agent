import json
import re
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
import operator
import os

# ─────────────────────────────────────────────
# 1. LOAD KNOWLEDGE BASE (RAG)
# ─────────────────────────────────────────────

def load_knowledge_base(path="knowledge_base.json"):
    with open(path, "r") as f:
        return json.load(f)

KB = load_knowledge_base()

def retrieve_from_kb(query: str) -> str:
    """Simple RAG: match keywords and return relevant KB section as text."""
    query_lower = query.lower()
    results = []

    if any(word in query_lower for word in ["price", "pricing", "plan", "cost", "basic", "pro", "how much"]):
        basic = KB["pricing"]["basic_plan"]
        pro = KB["pricing"]["pro_plan"]
        results.append(
            f"**AutoStream Pricing:**\n"
            f"- Basic Plan: {basic['price']} — {basic['videos_per_month']} videos/month, {basic['resolution']} resolution\n"
            f"- Pro Plan: {pro['price']} — {pro['videos_per_month']} videos/month, {pro['resolution']} resolution, includes AI captions & 24/7 support"
        )

    if any(word in query_lower for word in ["refund", "cancel", "policy", "money back"]):
        results.append(f"**Refund Policy:** {KB['policies']['refund_policy']}")

    if any(word in query_lower for word in ["support", "help", "contact"]):
        results.append(f"**Support Policy:** {KB['policies']['support']}")

    if any(word in query_lower for word in ["what is autostream", "about", "company", "tell me about"]):
        results.append(f"**About AutoStream:** {KB['company']['description']} — \"{KB['company']['tagline']}\"")

    return "\n\n".join(results) if results else ""


# ─────────────────────────────────────────────
# 2. MOCK LEAD CAPTURE TOOL
# ─────────────────────────────────────────────

def mock_lead_capture(name: str, email: str, platform: str):
    print("\n" + "="*50)
    print(f"✅ Lead captured successfully: {name}, {email}, {platform}")
    print("="*50 + "\n")
    return f"Lead captured: {name} | {email} | {platform}"


# ─────────────────────────────────────────────
# 3. LANGGRAPH STATE DEFINITION
# ─────────────────────────────────────────────

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    intent: str                  # "greeting" | "inquiry" | "high_intent"
    lead_name: str
    lead_email: str
    lead_platform: str
    lead_captured: bool
    awaiting: str                # what info we're currently waiting for


# ─────────────────────────────────────────────
# 4. LLM SETUP (Gemini 1.5 Flash)
# ─────────────────────────────────────────────

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.environ.get("OPENAI_API_KEY"),
    temperature=0.3
)


# ─────────────────────────────────────────────
# 5. NODE: INTENT DETECTION
# ─────────────────────────────────────────────

def detect_intent(state: AgentState) -> AgentState:
    last_message = state["messages"][-1].content.lower()

    high_intent_keywords = [
        "sign up", "sign me up", "i want to try", "i want to subscribe",
        "let's do it", "ready to start", "i'll take", "i want the pro",
        "i want the basic", "get started", "purchase", "buy", "subscribe"
    ]
    greeting_keywords = ["hi", "hello", "hey", "good morning", "good evening", "howdy"]

    if any(kw in last_message for kw in high_intent_keywords):
        state["intent"] = "high_intent"
    elif any(kw in last_message for kw in greeting_keywords) and len(last_message.split()) <= 6:
        state["intent"] = "greeting"
    else:
        state["intent"] = "inquiry"

    return state


# ─────────────────────────────────────────────
# 6. NODE: GENERATE RESPONSE
# ─────────────────────────────────────────────

def generate_response(state: AgentState) -> AgentState:
    intent = state["intent"]
    user_message = state["messages"][-1].content
    awaiting = state.get("awaiting", "")

    # ── If we are in lead collection mode ──
    if awaiting == "name":
        state["lead_name"] = user_message.strip()
        state["awaiting"] = "email"
        reply = "Got it! Now, could you please share your **email address**?"

    elif awaiting == "email":
        email = user_message.strip()
        # Basic email validation
        if "@" not in email or "." not in email.split("@")[-1]:
            reply = "That doesn't look like a valid email. Could you double-check and re-enter it?"
        else:
            state["lead_email"] = email
            state["awaiting"] = "platform"
            reply = "Almost there! Which **creator platform** do you primarily use? (e.g., YouTube, Instagram, TikTok, Twitch)"

    elif awaiting == "platform":
        state["lead_platform"] = user_message.strip()
        state["awaiting"] = ""
        # All three collected — fire the tool
        result = mock_lead_capture(state["lead_name"], state["lead_email"], state["lead_platform"])
        state["lead_captured"] = True
        reply = (
            f"🎉 You're all set, **{state['lead_name']}**!\n\n"
            f"We've captured your details and our team will reach out to your **{state['lead_platform']}** account email shortly.\n\n"
            f"Welcome to AutoStream Pro — let's create something amazing! 🚀"
        )

    # ── Intent-based responses ──
    elif intent == "greeting":
        reply = (
            "Hey there! 👋 Welcome to **AutoStream** — your automated video editing co-pilot!\n\n"
            "I can help you with:\n"
            "- 📦 Pricing & Plans\n"
            "- 🔧 Features & Capabilities\n"
            "- 📋 Company Policies\n"
            "- ✍️ Getting you signed up!\n\n"
            "What would you like to know?"
        )

    elif intent == "high_intent":
        # Start lead collection
        state["awaiting"] = "name"
        kb_context = retrieve_from_kb(user_message)
        reply = (
            "That's awesome! 🙌 I'd love to get you started.\n\n"
            "Let me just grab a few quick details to set up your account.\n\n"
            "First — what's your **full name**?"
        )

    else:
        # RAG-powered inquiry
        kb_context = retrieve_from_kb(user_message)

        if kb_context:
            prompt = (
                f"You are a friendly and helpful sales assistant for AutoStream, a SaaS video editing platform.\n\n"
                f"Use ONLY the following knowledge base information to answer the user's question. "
                f"Do not make up any details. Be concise and helpful.\n\n"
                f"Knowledge Base:\n{kb_context}\n\n"
                f"User Question: {user_message}\n\n"
                f"Answer:"
            )
        else:
            prompt = (
                f"You are a friendly sales assistant for AutoStream, an automated video editing SaaS.\n"
                f"The user asked: '{user_message}'\n"
                f"You don't have specific data on this. Politely say you don't have that info and "
                f"suggest they visit autostream.io or ask about pricing/features."
            )

        response = llm.invoke([HumanMessage(content=prompt)])
        reply = response.content

    state["messages"].append(AIMessage(content=reply))
    return state


# ─────────────────────────────────────────────
# 7. ROUTING LOGIC
# ─────────────────────────────────────────────

def should_continue(state: AgentState) -> str:
    if state.get("lead_captured"):
        return END
    return "generate_response"


# ─────────────────────────────────────────────
# 8. BUILD THE LANGGRAPH
# ─────────────────────────────────────────────

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("detect_intent", detect_intent)
    graph.add_node("generate_response", generate_response)

    graph.set_entry_point("detect_intent")
    graph.add_edge("detect_intent", "generate_response")
    graph.add_conditional_edges(
        "generate_response",
        should_continue,
        {END: END, "generate_response": END}   # always END after one turn
    )

    return graph.compile()


# ─────────────────────────────────────────────
# 9. MAIN CHAT LOOP
# ─────────────────────────────────────────────

def main():
    print("\n🎬 Welcome to AutoStream AI Agent")
    print("Type 'quit' or 'exit' to stop.\n")
    print("-" * 50)

    app = build_graph()

    # Persistent state across turns
    state: AgentState = {
        "messages": [],
        "intent": "",
        "lead_name": "",
        "lead_email": "",
        "lead_platform": "",
        "lead_captured": False,
        "awaiting": ""
    }

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["quit", "exit"]:
            print("Agent: Thanks for chatting! Have a great day! 👋")
            break

        # Add user message to state
        state["messages"].append(HumanMessage(content=user_input))

        # Run graph
        state = app.invoke(state)

        # Print last agent message
        agent_reply = state["messages"][-1].content
        print(f"\nAgent: {agent_reply}\n")
        print("-" * 50)

        # Stop if lead captured
        if state.get("lead_captured"):
            break


if __name__ == "__main__":
    main()