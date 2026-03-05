import streamlit as st
import os
import json
import sys
# Version: 1.0.2 (Force Refresh + Metadata Fix)
from phase3.bot import INDmoneyBot

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="INDmoney RAG Assistant",
    page_icon="🤖",
    layout="centered"
)

# --- CUSTOM CSS (Glassmorphism & Premium Look) ---
st.markdown("""
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Outfit:wght@400;600;800&display=swap');

    :root {
        --primary: #5567ff;
        --bg-dark: #0d0e14;
        --bg-glass: rgba(255, 255, 255, 0.05);
        --border-glass: rgba(255, 255, 255, 0.1);
        --text-main: #ffffff;
    }

    .stApp {
        background: radial-gradient(circle at top left, #1a1c2c, #0d0e14);
        color: var(--text-main) !important;
        font-family: 'Inter', sans-serif;
    }

    /* Force white text for all markdown/standard text */
    .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3 {
        color: #ffffff !important;
    }

    /* Fix Streamlit Chat Message text color */
    [data-testid="stChatMessage"] div {
        color: #ffffff !important;
    }

    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }

    /* Glassmorphism Container */
    .main-container {
        background: var(--bg-glass);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border-glass);
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 0 40px 100px rgba(0, 0, 0, 0.5);
    }

    /* Header Styling */
    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border-glass);
    }

    .logo-area {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .logo-icon {
        width: 32px;
        height: 32px;
        background: var(--primary);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-family: 'Outfit', sans-serif;
        font-size: 18px;
        color: white !important;
    }

    h1 {
        font-family: 'Outfit', sans-serif;
        font-size: 24px;
        font-weight: 600;
        margin: 0;
        color: white !important;
    }

    .status-area {
        font-size: 12px;
        color: #4ade80 !important;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        background: #4ade80;
        border-radius: 50%;
        box-shadow: 0 0 10px #4ade80;
    }

    /* Source Link Styling */
    .source-link {
        display: block;
        margin-top: 10px;
        font-size: 12px;
        color: var(--primary) !important;
        text-decoration: none;
        font-weight: 600;
    }

    /* Fix Suggested Buttons (Streamlit Native) */
    button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid var(--border-glass) !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        font-size: 12px !important;
        padding: 0.5rem 1rem !important;
        height: auto !important;
    }
    button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: var(--primary) !important;
    }

    /* Typing Indicator (CSS only) */
    .typing {
        font-size: 12px;
        color: #b0b0b0 !important;
        margin-bottom: 10px;
        font-style: italic;
    }

    /* Chat input custom styling */
    .stChatInputContainer {
        border-radius: 14px !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid var(--border-glass) !important;
    }

    /* Force input text color */
    .stChatInputContainer textarea {
        color: #ffffff !important;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- BOT INITIALIZATION ---
@st.cache_resource
def get_bot():
    bot_instance = INDmoneyBot()
    # Auto-initialize if collection is empty (crucial for Streamlit Cloud)
    if bot_instance.collection.count() == 0:
        with st.spinner("Initializing Mutual Fund database..."):
            from phase2.ingest import ingest_to_vector_db
            json_path = os.path.join(os.getcwd(), "phase1", "fund_data.json")
            ingest_to_vector_db(json_path)
            # Re-initialize collection reference after ingestion
            bot_instance.collection = bot_instance.client.get_collection("fund_data")
    return bot_instance

bot = get_bot()

# --- STATUS HELPER ---
def get_last_update():
    json_path = os.path.join(os.getcwd(), "phase1", "fund_data.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                if data:
                    first_fund = next(iter(data.values()))
                    return first_fund.get('nav_date', 'N/A')
        except:
            pass
    return "N/A"

last_update = get_last_update()

# --- UI HEADER ---
st.markdown(f"""
    <div class="app-header">
        <div class="logo-area">
            <div class="logo-icon">I</div>
            <h1>INDmoney RAG Assistant</h1>
        </div>
        <div class="status-area">
            <div class="status-dot"></div>
            <span>v1.2 | Live Data | Last Updated: {last_update}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- SESSION STATE (Chat History) ---
if "messages" not in st.session_state:
    supported_funds_md = """# Welcome to INDmoney RAG Assistant! 📈
I can provide factual details (NAV, AUM, Expense Ratio, etc.) for these specific funds:

✅ **ICICI Prudential Large Cap Fund**
✅ **HDFC Flexi Cap Fund**
✅ **Kotak Large Cap Fund**
✅ **Bank of India Flexi Cap Fund**
✅ **HDFC Small Cap Fund**
✅ **Mahindra Manulife Mid Cap Fund**
✅ **Motilal Oswal Large and Midcap Fund**

---
**How can I help you today?**"""
    
    st.session_state.messages = [{
        "role": "assistant",
        "content": supported_funds_md
    }]

# --- DISPLAY CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        content = message["content"]
        if "Source:" in content and message["role"] == "assistant":
            parts = content.split("Source:")
            st.markdown(parts[0].strip())
            st.markdown(f'<a href="{parts[1].strip()}" class="source-link" target="_blank">View Source on INDmoney.com →</a>', unsafe_allow_html=True)
        else:
            st.markdown(content)

# --- SUGGESTED QUESTIONS ---
st.markdown("---")
cols = st.columns(3)
suggestions = [
    "What is the exit load of HDFC Small Cap?",
    "Tell me about ICICI Prudential Large Cap",
    "Who is the manager of Kotak Large Cap?"
]

def on_suggestion_click(q):
    st.session_state.user_input = q

for i, q in enumerate(suggestions):
    if cols[i].button(q, key=f"btn_{i}"):
        st.session_state.messages.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(q)
        
        with st.chat_message("assistant"):
            with st.spinner("Analyzing data..."):
                response = bot.handle_query(q)
                st.session_state.messages.append({"role": "assistant", "content": response})
                if "Source:" in response:
                    parts = response.split("Source:")
                    st.markdown(parts[0].strip())
                    st.markdown(f'<a href="{parts[1].strip()}" class="source-link" target="_blank">View Source on INDmoney.com →</a>', unsafe_allow_html=True)
                else:
                    st.markdown(response)
        st.rerun()

# --- CHAT INPUT ---
if prompt := st.chat_input("Ask about Mutual Funds (e.g. NAV, Exit Load)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing data..."):
            response = bot.handle_query(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            if "Source:" in response:
                parts = response.split("Source:")
                st.markdown(parts[0].strip())
                st.markdown(f'<a href="{parts[1].strip()}" class="source-link" target="_blank">View Source on INDmoney.com →</a>', unsafe_allow_html=True)
            else:
                st.markdown(response)
