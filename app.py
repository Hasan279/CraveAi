import streamlit as st
import os
import sys
from dotenv import load_dotenv
from google import genai

# Load secrets: .env locally, st.secrets on Streamlit Cloud
load_dotenv()
if not os.getenv("GEMINI_API_KEY") and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]


# Fix Windows console encoding for emoji printing
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ── Imports from existing project files ──────────────────────────────
from shared_functions import (
    load_food_data,
    create_similarity_search_collection,
    populate_similarity_collection,
    perform_similarity_search,
    perform_filtered_similarity_search,
)
from enhanced_rag_chatbot import (
    generate_llm_rag_response,
    generate_llm_comparison,
    prepare_context_for_llm,
    generate_fallback_response,
)

# ── Page config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="CraveAI — Smart Food Recommendations",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Import Google Fonts ─────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');

/* ── Root variables (Gemini Dark Theme) ─────────────────── */
:root {
    --bg-primary: #131314;
    --bg-card: #1e1f20;
    --text-primary: #e3e3e3;
    --text-muted: #c4c7c5;
    --border: #333538;
    --accent-blue: #a8c7fa;
    --gemini-gradient: linear-gradient(74deg, #4285f4 0, #9b72cb 9%, #d96570 20%, #d96570 24%, #9b72cb 35%, #4285f4 44%);
}

html, body, [data-testid="stApp"] {
    font-family: 'Google Sans', 'Outfit', sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* ── Sidebar ────────────────────────────────────────────── */
/* ── Sidebar ────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background-color: #1a1b1c !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: 4px 0 16px rgba(0,0,0,0.3) !important;
}

section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--text-primary) !important;
    font-family: 'Google Sans', sans-serif;
}

/* Sidebar Brand */
.sidebar-brand {
    font-size: 3.5rem !important;
    font-weight: 700;
    background: var(--gemini-gradient);
    background-size: 400% 100%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradient-shift 8s ease infinite;
    margin: 0;
    padding: 0;
}

/* Sidebar Buttons Depth */
section[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(145deg, #242526, #1e1f20) !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
    border: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    box-shadow: 0 6px 12px rgba(0,0,0,0.4) !important;
    transform: translateY(-1px);
}

/* Sidebar Quit Button (Primary) */
section[data-testid="stSidebar"] button[kind="primary"],
section[data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"],
div[data-testid="stSidebar"] button[kind="primary"] {
    background-color: #d93025 !important;
    background: #d93025 !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 4px 6px rgba(217, 48, 37, 0.3) !important;
}
section[data-testid="stSidebar"] button[kind="primary"]:hover,
section[data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"]:hover,
div[data-testid="stSidebar"] button[kind="primary"]:hover {
    background-color: #c5221f !important;
    background: #c5221f !important;
    box-shadow: 0 6px 12px rgba(217, 48, 37, 0.5) !important;
}


/* ── Chat bubbles ───────────────────────────────────────── */
/* Base Chat Message */
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border: none !important;
    padding: 1rem 0 !important;
    margin-bottom: 0 !important;
}

/* User Message */
[data-testid="stChatMessage"][data-baseweb="block"]:nth-child(odd) {
    background-color: #1e1f20 !important;
    border-radius: 24px !important;
    padding: 1rem 1.5rem !important;
    margin: 1rem 0 !important;
    width: fit-content !important;
    max-width: 80% !important;
    margin-left: auto !important;
}

/* Assistant Message */
[data-testid="stChatMessage"][data-baseweb="block"]:nth-child(even) {
    background-color: transparent !important;
}

/* ── Buttons ────────────────────────────────────────────── */
.stButton > button {
    background-color: #1e1f20 !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 24px !important;
    font-weight: 500 !important;
    font-family: 'Google Sans', sans-serif !important;
    transition: background-color 0.2s ease !important;
}
.stButton > button:hover {
    background-color: #333538 !important;
    border-color: #444746 !important;
}

/* Primary Button */
.stButton > button[data-testid="baseButton-primary"] {
    background-color: var(--accent-blue) !important;
    color: #041e49 !important;
    border: none !important;
}
.stButton > button[data-testid="baseButton-primary"]:hover {
    background-color: #b5d0fc !important;
}

/* ── Expanders ──────────────────────────────────────────── */
details {
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    background-color: var(--bg-card) !important;
}

/* ── Hero banner (Gemini Style) ─────────────────────────── */
.hero-banner {
    padding: 4rem 1rem 2rem 1rem;
    text-align: left;
}
.gemini-greeting {
    font-size: 3.5rem;
    font-weight: 500;
    line-height: 1.1;
    margin-bottom: 0.5rem;
    font-family: 'Google Sans', sans-serif;
    letter-spacing: -1px;
}
.gemini-gradient {
    background: var(--gemini-gradient);
    background-size: 400% 100%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradient-shift 8s ease infinite;
}
.gemini-subtitle {
    font-size: 3.5rem;
    font-weight: 500;
    line-height: 1.1;
    color: #444746;
    margin-top: 0;
    font-family: 'Google Sans', sans-serif;
    letter-spacing: -1px;
}

@keyframes gradient-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ── Typing Indicator ───────────────────────────────────── */
.typing-indicator {
    display: inline-flex;
    align-items: center;
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 14px 20px;
    margin-bottom: 1rem;
    gap: 6px;
}
.typing-dot {
    width: 8px;
    height: 8px;
    background-color: var(--text-muted);
    border-radius: 50%;
    animation: typing-bounce 1.4s infinite ease-in-out both;
}
.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing-bounce {
    0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
    40% { transform: scale(1); opacity: 1; }
}

/* ── Result card ────────────────────────────────────────── */
.result-card {
    background-color: #1e1f20;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    transition: background-color 0.2s ease;
}
.result-card:hover {
    background-color: #282a2c;
}
.result-card h4 {
    margin: 0 0 .5rem;
    font-weight: 500;
    color: var(--text-primary);
    font-family: 'Google Sans', sans-serif;
}
.result-card .meta {
    display: flex;
    gap: 1rem;
    font-size: .85rem;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
}
.result-card .desc {
    font-size: .9rem;
    color: var(--text-muted);
    line-height: 1.4;
}

/* Hide Streamlit Top Padding */
.block-container {
    padding-top: 2rem !important;
}

/* Text Input Styling */
.stTextInput > div > div > input {
    background-color: #1e1f20 !important;
    border: 1px solid var(--border) !important;
    border-radius: 24px !important;
    color: var(--text-primary) !important;
    padding: 1rem 1.5rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #444746 !important;
    box-shadow: none !important;
}

/* Chat Input Styling */
[data-testid="stChatInput"] {
    background-color: #1e1f20 !important;
    border: 2px solid var(--border) !important;
    border-radius: 32px !important;
    padding: 0 !important;
    overflow: hidden !important;
}

/* Gemini gradient border on focus */
[data-testid="stChatInput"]:focus-within {
    border-color: transparent !important;
    background: linear-gradient(#1e1f20, #1e1f20) padding-box, 
                var(--gemini-gradient) border-box !important;
}

/* Kill all internal borders, shadows, and conflicting shapes */
[data-testid="stChatInput"] div,
[data-testid="stChatInput"] svg {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    background-color: transparent !important;
}

[data-testid="stChatInput"] textarea {
    color: var(--text-primary) !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    padding: 1rem 1.5rem !important;
}

[data-testid="stChatInput"] button {
    color: var(--text-primary) !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    background-color: transparent !important;
}
</style>
""", unsafe_allow_html=True)


# ── Query rewriter (reuses genai already configured in enhanced_rag_chatbot) ─
def rewrite_query(prompt: str, messages: list) -> str:
    """Use the LLM to rewrite the user's message into an optimal vector-DB query."""
    client = genai.Client() # Uses GEMINI_API_KEY from environment

    history = []
    for msg in messages[-6:]:
        if msg["role"] != "assistant" or "results" not in msg:
            history.append(f"{msg['role'].capitalize()}: {msg['content']}")
    history_text = "\n".join(history)

    rewrite_prompt = f"""You are a query rewriter for a food recommendation vector database.
Here is the recent conversation:
{history_text}

Current user message: "{prompt}"

Rewrite this into an effective semantic search query.
Rules:
- If the user uses negations ("NOT sweet", "no meat"), replace them with positive descriptors ("savory salty tangy", "vegetarian plant-based").
- If it is a follow-up, merge context from earlier messages.
- Output ONLY the rewritten query, nothing else."""

    try:
        resp = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=rewrite_prompt
        )
        if resp and resp.text:
            return resp.text.strip()
    except Exception:
        pass
    return prompt


# ── Database initialisation (cached) ────────────────────────────────
@st.cache_resource(show_spinner=False)
def setup_database():
    try:
        _here = os.path.dirname(os.path.abspath(__file__))
        food_items = load_food_data(os.path.join(_here, 'FoodDataset.json'))
        collection = create_similarity_search_collection(
            "craveai_collection",
            {"description": "CraveAI Streamlit RAG chatbot collection"},
        )
        populate_similarity_collection(collection, food_items)
        return collection, food_items
    except Exception as e:
        import traceback
        with open("setup_error.log", "w") as f:
            f.write(traceback.format_exc())
        raise e

with st.spinner("Loading food database & building vector index…"):
    collection, food_items = setup_database()

# ── Session state defaults ───────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "compare_mode" not in st.session_state:
    st.session_state.compare_mode = False
if "compare_q1" not in st.session_state:
    st.session_state.compare_q1 = ""

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 class='sidebar-brand'>CraveAI</h2>", unsafe_allow_html=True)
    st.caption("Intelligent food recommendations powered by RAG")
    st.divider()

    # Controls
    with st.expander("Controls"):
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.compare_mode = False
            st.session_state.compare_q1 = ""
            st.rerun()

        compare_toggle = st.toggle("Comparison Mode", value=st.session_state.compare_mode,
                                   help="Compare recommendations for two different cravings side-by-side.")
        st.session_state.compare_mode = compare_toggle

    st.divider()

    # Quick suggestions
    st.markdown("### Try asking")
    suggestions = [
        "Spicy dinner under 400 cal",
        "Healthy Italian pasta",
        "Comfort food for a cold night",
        "High-protein breakfast",
    ]
    for s in suggestions:
        if st.button(s, key=f"sug_{s}", use_container_width=True):
            st.session_state.pending_suggestion = s
            st.rerun()

    st.divider()

    # Quit button
    st.markdown('''
        <style>
        /* Force Red for the last primary button in the sidebar */
        [data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"] {
            background-color: #d93025 !important;
            color: #ffffff !important;
        }
        </style>
    ''', unsafe_allow_html=True)
    if st.button("Stop Server & Quit", use_container_width=True, type="primary"):
        st.markdown("**Goodbye!** Please close the terminal window to stop the server.")
        # Gracefully stop the Streamlit server
        # os._exit(0)


# ── Hero Banner ──────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="hero-banner">
        <h1 class="gemini-greeting"><span class="gemini-gradient">Hello there.</span></h1>
        <h2 class="gemini-subtitle">What are you craving today?</h2>
        <p style="color: var(--text-muted); margin-top: 1rem; font-size: 1.1rem; font-weight: 400;">
            Searching through {} curated dishes to find exactly what you're looking for.
        </p>
    </div>
    """.format(len(food_items)), unsafe_allow_html=True)


# ── Render result cards (helper) ─────────────────────────────────────
def render_result_cards(results, max_show=3):
    """Render search results as styled HTML cards."""
    for idx, res in enumerate(results[:max_show], 1):
        score_pct = res["similarity_score"] * 100
        st.markdown(f"""
        <div class="result-card">
            <h4>{idx}. {res['food_name']}</h4>
            <div class="meta">
                <span>{res['cuisine_type']}</span>
                <span>{res['food_calories_per_serving']} cal</span>
                <span>{score_pct:.0f}% match</span>
            </div>
            <div class="desc">{res['food_description']}</div>
        </div>
        """, unsafe_allow_html=True)


# ── Comparison Mode UI ───────────────────────────────────────────────
if st.session_state.compare_mode:
    st.markdown("### Comparison Mode")
    st.caption("Enter two different food cravings and compare the results side-by-side.")

    c1, c2 = st.columns(2)
    query_a = c1.text_input("Craving A", placeholder="e.g. spicy Thai food")
    query_b = c2.text_input("Craving B", placeholder="e.g. light Italian salad")

    if st.button("Compare", use_container_width=True, type="primary"):
        if query_a.strip() and query_b.strip():
            typing_placeholder = st.empty()
            typing_placeholder.markdown('''
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            ''', unsafe_allow_html=True)
            
            res_a = perform_similarity_search(collection, query_a.strip(), 3)
            res_b = perform_similarity_search(collection, query_b.strip(), 3)
            comparison_text = generate_llm_comparison(query_a, query_b, res_a, res_b)
            
            typing_placeholder.empty()

            st.markdown(f"**AI Analysis:**\n\n{comparison_text}")

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"#### Results for *\"{query_a}\"*")
                render_result_cards(res_a)
            with col_b:
                st.markdown(f"#### Results for *\"{query_b}\"*")
                render_result_cards(res_b)
        else:
            st.warning("Please enter both cravings to compare.")

    st.divider()


# ── Chat history display ─────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "results" in message and message["results"]:
            with st.expander("Detailed Search Results"):
                render_result_cards(message["results"])
                if "rewritten_query" in message:
                    st.caption(f"Optimised search query: *{message['rewritten_query']}*")

# ── Process pending suggestion (from sidebar button) ─────────────────
if "pending_suggestion" in st.session_state:
    prompt = st.session_state.pop("pending_suggestion")

    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown('''
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        ''', unsafe_allow_html=True)
        
        rewritten = rewrite_query(prompt, st.session_state.messages)
        search_results = perform_similarity_search(collection, rewritten, 5)

        typing_placeholder.empty()

        if not search_results:
            resp = "Hmm, I couldn't find a match for that. Could you try rephrasing?"
            st.markdown(resp)
            st.session_state.messages.append({"role": "assistant", "content": resp})
        else:
            ai_resp = generate_llm_rag_response(prompt, search_results)
            st.markdown(ai_resp)
            with st.expander("Detailed Search Results"):
                render_result_cards(search_results)
                st.caption(f"Optimised search query: *{rewritten}*")
            st.session_state.messages.append({
                "role": "assistant",
                "content": ai_resp,
                "results": search_results,
                "rewritten_query": rewritten,
            })

# ── Chat input ───────────────────────────────────────────────────────
if prompt := st.chat_input("What are you craving today?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown('''
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        ''', unsafe_allow_html=True)
        
        rewritten = rewrite_query(prompt, st.session_state.messages)
        search_results = perform_similarity_search(collection, rewritten, 5)

        typing_placeholder.empty()

        if not search_results:
            resp = "Hmm, I couldn't find a match for that. Could you try rephrasing?"
            st.markdown(resp)
            st.session_state.messages.append({"role": "assistant", "content": resp})
        else:
            ai_resp = generate_llm_rag_response(prompt, search_results)
            st.markdown(ai_resp)
            with st.expander("Detailed Search Results"):
                render_result_cards(search_results)
                st.caption(f"Optimised search query: *{rewritten}*")
            st.session_state.messages.append({
                "role": "assistant",
                "content": ai_resp,
                "results": search_results,
                "rewritten_query": rewritten,
            })
