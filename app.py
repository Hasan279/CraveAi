import streamlit as st
import os
import sys
import base64
from dotenv import load_dotenv
from google import genai

# Load secrets: .env locally, st.secrets on Streamlit Cloud
load_dotenv()
if not os.getenv("GEMINI_API_KEY") and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]


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

# ── Avatar definitions ───────────────────────────────────────────────
_user_svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36"><circle cx="18" cy="18" r="18" fill="#1e1f20"/><circle cx="18" cy="13" r="6" fill="#a8c7fa"/><ellipse cx="18" cy="30" rx="12" ry="8" fill="#a8c7fa"/></svg>'
_bot_svg  = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36"><circle cx="18" cy="18" r="18" fill="#1e1f20"/><path d="M18 7l2.5 8.5L29 18l-8.5 2.5L18 29l-2.5-8.5L7 18l8.5-2.5Z" fill="url(#g)"/><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#4285f4"/><stop offset="50%" stop-color="#9b72cb"/><stop offset="100%" stop-color="#d96570"/></linearGradient></defs></svg>'
USER_AVATAR = f"data:image/svg+xml;base64,{base64.b64encode(_user_svg.encode()).decode()}"
BOT_AVATAR  = f"data:image/svg+xml;base64,{base64.b64encode(_bot_svg.encode()).decode()}"

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

html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"], [data-testid="stMainBlockContainer"], [data-testid="stBottom"], [data-testid="stBottom"] > div, [data-testid="stBottomBlockContainer"], .main, .block-container {
    font-family: 'Google Sans', 'Outfit', sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

footer {
    visibility: hidden;
}

/* Force legible placeholder colors on text inputs */
input::placeholder {
    color: #c4c7c5 !important;
    -webkit-text-fill-color: #c4c7c5 !important;
    opacity: 0.7 !important;
}

textarea::placeholder {
    color: #c4c7c5 !important;
    -webkit-text-fill-color: #c4c7c5 !important;
    opacity: 0.7 !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #c4c7c5 !important;
    -webkit-text-fill-color: #c4c7c5 !important;
    opacity: 0.7 !important;
}

[data-testid="stChatInput"] textarea::-webkit-input-placeholder {
    color: #c4c7c5 !important;
    -webkit-text-fill-color: #c4c7c5 !important;
    opacity: 0.7 !important;
}

/* Force light text color on widgets, widgets labels, sidebar text/span, and captions */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] small,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span {
    color: var(--text-primary);
}

/* Captions should be muted color */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionText"],
.stCaptionContainer,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stCaptionText"] {
    color: var(--text-muted) !important;
}

/* Expander headers */
details summary span,
details summary p,
details summary div {
    color: var(--text-primary) !important;
}

/* Make sure sidebar brand overrides general color rules to stay gradient */
.sidebar-brand {
    color: transparent !important;
    -webkit-text-fill-color: transparent !important;
}


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
    text-align: center;
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

/* ── Blob Thinking Indicator ─────────────────────────────── */
.blob-thinking {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 82px;
    height: 52px;
    background: linear-gradient(135deg, #1e1f20, #2a2b2d);
    border: 1px solid var(--border);
    border-radius: 50% 40% 60% 30% / 40% 50% 30% 60%;
    animation: blob-morph 3s ease-in-out infinite;
    gap: 5px;
    margin-bottom: 1rem;
    box-shadow: 0 4px 20px rgba(66, 133, 244, 0.12);
}

@keyframes blob-morph {
    0%,100% { border-radius: 50% 40% 60% 30% / 40% 50% 30% 60%; }
    25%     { border-radius: 30% 60% 40% 70% / 60% 30% 70% 40%; }
    50%     { border-radius: 70% 30% 50% 50% / 30% 70% 40% 60%; }
    75%     { border-radius: 40% 60% 30% 70% / 50% 30% 60% 40%; }
}

.blob-dot {
    width: 7px;
    height: 7px;
    background: var(--accent-blue);
    border-radius: 50%;
    animation: blob-dot-pulse 1.4s infinite ease-in-out both;
    flex-shrink: 0;
}
.blob-dot:nth-child(1) { animation-delay: -0.32s; }
.blob-dot:nth-child(2) { animation-delay: -0.16s; }
.blob-dot:nth-child(3) { animation-delay: 0s; }

@keyframes blob-dot-pulse {
    0%, 80%, 100% { transform: scale(0.5); opacity: 0.4; }
    40%           { transform: scale(1.1); opacity: 1; }
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
            typing_placeholder.markdown('<div class="blob-thinking"><div class="blob-dot"></div><div class="blob-dot"></div><div class="blob-dot"></div></div>', unsafe_allow_html=True)
            
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
    with st.chat_message(message["role"], avatar=USER_AVATAR if message["role"] == "user" else BOT_AVATAR):
        st.markdown(message["content"])
        if "results" in message and message["results"]:
            with st.expander("Detailed Search Results"):
                render_result_cards(message["results"])
                if "rewritten_query" in message:
                    st.caption(f"Optimised search query: *{message['rewritten_query']}*")

# ── Process pending suggestion (from sidebar button) ─────────────────
if "pending_suggestion" in st.session_state:
    prompt = st.session_state.pop("pending_suggestion")

    st.chat_message("user", avatar=USER_AVATAR).markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        typing_placeholder = st.empty()
        typing_placeholder.markdown('<div class="blob-thinking"><div class="blob-dot"></div><div class="blob-dot"></div><div class="blob-dot"></div></div>', unsafe_allow_html=True)
        
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
    st.chat_message("user", avatar=USER_AVATAR).markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        typing_placeholder = st.empty()
        typing_placeholder.markdown('<div class="blob-thinking"><div class="blob-dot"></div><div class="blob-dot"></div><div class="blob-dot"></div></div>', unsafe_allow_html=True)
        
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
