"""DrJhaGPT — an open-source RAG chatbot with a brand-matched editorial UI.

Stack: Groq (open LLMs) for generation + retrieval over drpranayjha.com content.
Visual design mirrors drpranayjha.com: white editorial theme, Inter/Oswald type,
charcoal ink (#141618) with a red accent (#ce242c).
"""
import base64
from functools import lru_cache

import streamlit as st

from chatbot import config, llm, rag

# ----------------------------------------------------------------------------- assets
@lru_cache(maxsize=1)
def logo_data_uri() -> str:
    if not config.LOGO_PATH.exists():
        return ""
    b64 = base64.b64encode(config.LOGO_PATH.read_bytes()).decode()
    return f"data:image/png;base64,{b64}"


@lru_cache(maxsize=1)
def logo_image():
    """PIL image for the page icon and assistant avatar (falls back to emoji)."""
    try:
        from PIL import Image

        return Image.open(config.LOGO_PATH)
    except Exception:
        return "🤖"


USER_AVATAR = "👤"

SUGGESTIONS = [
    "What is VMware HCX and when should I use it?",
    "Give me a VCF 9 pre-installation checklist",
    "How do I size infrastructure for an AI workload?",
    "vSphere HA vs DRS — what's the difference?",
]

st.set_page_config(
    page_title=config.BRAND_NAME,
    page_icon=logo_image(),
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------------------------------- styling
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Oswald:wght@500;600;700&display=swap');

:root {
  --ink: #141618; --accent: #ce242c; --accent-dark: #a81d24;
  --muted: #5f5e5a; --panel: #f5f5f5; --border: #e7e7e7;
}

/* Base type + background */
html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; color: var(--ink); }
.stApp { background: #ffffff; }

/* Hide Streamlit chrome for a production look */
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"],
#MainMenu, footer { display: none !important; }
header[data-testid="stHeader"] { background: transparent; height: 0; }

.block-container { max-width: 800px; padding-top: 1.6rem; padding-bottom: 6rem; }

/* ---- Masthead ---- */
.dj-masthead { display: flex; align-items: center; gap: 16px; }
.dj-masthead img { width: 56px; height: 56px; border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,.12); }
.dj-eyebrow { font-family: 'Oswald', sans-serif; color: var(--accent); font-size: 11px;
              letter-spacing: 3px; font-weight: 600; text-transform: uppercase; margin: 0; }
.dj-title { font-family: 'Oswald', sans-serif; color: var(--ink); font-size: 30px;
            font-weight: 700; letter-spacing: .3px; line-height: 1.05; margin: 2px 0 0; }
.dj-title .accent { color: var(--accent); }
.dj-tagline { color: var(--muted); font-size: 13.5px; margin: 6px 0 0; }
.dj-rule { height: 3px; background: var(--accent); width: 54px; border: 0; margin: 14px 0 4px;
           border-radius: 2px; }

/* ---- Chat messages ---- */
[data-testid="stChatMessage"] { background: transparent; padding: .35rem 0; }
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li { font-size: 15.5px; line-height: 1.7; }
[data-testid="stChatMessage"] a { color: var(--accent); text-decoration: none; border-bottom: 1px solid rgba(206,36,44,.35); }
[data-testid="stChatMessage"] a:hover { border-bottom-color: var(--accent); }
[data-testid="stChatMessage"] h1, [data-testid="stChatMessage"] h2, [data-testid="stChatMessage"] h3 {
  font-family: 'Oswald', sans-serif; color: var(--ink); letter-spacing: .2px; margin-top: .4rem; }
[data-testid="stChatMessageAvatarUser"] { background: var(--ink) !important; }

/* ---- "Related reading" source cards ---- */
.dj-sources { margin: 14px 0 2px; }
.dj-sources-label { font-family: 'Oswald', sans-serif; color: var(--accent); font-size: 11px;
                    letter-spacing: 2.5px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; }
.dj-source { display: flex; flex-direction: column; gap: 2px; text-decoration: none !important;
             border: 1px solid var(--border); border-left: 3px solid var(--accent);
             border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; background: #fff;
             transition: background .15s, box-shadow .15s, transform .15s; }
.dj-source:hover { background: var(--panel); box-shadow: 0 2px 10px rgba(20,22,24,.06); transform: translateY(-1px); }
.dj-source-title { color: var(--ink) !important; font-weight: 600; font-size: 14px; }
.dj-source-host { color: var(--muted); font-size: 12px; }

/* ---- Suggestion chips (empty state) ---- */
.dj-intro { color: var(--muted); font-size: 14.5px; margin: 6px 0 14px; }
div[data-testid="stButton"] > button {
  border: 1px solid var(--border); background: #fff; color: var(--ink);
  border-radius: 999px; padding: 8px 16px; font-size: 13.5px; font-weight: 500;
  text-align: left; transition: all .15s; }
div[data-testid="stButton"] > button:hover {
  border-color: var(--accent); color: var(--accent); background: #fff; }

/* ---- Chat input ---- */
[data-testid="stChatInput"] { border-color: var(--border) !important; }
[data-testid="stChatInput"]:focus-within { border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px rgba(206,36,44,.12) !important; }

/* ---- Sidebar ---- */
[data-testid="stSidebar"] { background: var(--panel); border-right: 1px solid var(--border); }
</style>
""",
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------- components
def render_header():
    logo = logo_data_uri()
    img = f'<img src="{logo}" alt="logo">' if logo else ""
    st.markdown(
        f"""
        <div class="dj-masthead">
          {img}
          <div>
            <p class="dj-eyebrow">{config.BRAND_EYEBROW}</p>
            <h1 class="dj-title">DrJha<span class="accent">GPT</span></h1>
          </div>
        </div>
        <p class="dj-tagline">{config.BRAND_TAGLINE}</p>
        <hr class="dj-rule">
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    with st.sidebar:
        st.markdown(f"### {config.BRAND_NAME}")
        st.caption("Grounded in Dr. Pranay Jha's published work on VMware, "
                   "cloud, datacenters & AI.")
        st.markdown(f"🌐 [drpranayjha.com]({config.WEBSITE_URL})")
        st.divider()
        st.caption(f"Model: `{config.GROQ_MODEL}` · via Groq")
        st.caption("Knowledge base: " + ("✅ loaded" if rag.has_knowledge() else "⚠️ not built"))
        if st.button("Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


def render_sources(results):
    if not results:
        return
    seen, cards = set(), []
    for r in results:
        link, title = r.get("url"), r.get("title", "Article")
        if link and link not in seen:
            seen.add(link)
            cards.append(
                f'<a class="dj-source" href="{link}" target="_blank">'
                f'<span class="dj-source-title">{title}</span>'
                f'<span class="dj-source-host">drpranayjha.com ↗</span></a>'
            )
    if cards:
        st.markdown(
            '<div class="dj-sources"><div class="dj-sources-label">'
            'Related from drpranayjha.com</div>' + "".join(cards) + "</div>",
            unsafe_allow_html=True,
        )


def pick_suggestion(question: str):
    st.session_state.pending = question


def render_empty_state():
    st.markdown(
        '<p class="dj-intro">Ask a question, or start with one of these:</p>',
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for i, q in enumerate(SUGGESTIONS):
        cols[i % 2].button(q, key=f"sug_{i}", use_container_width=True,
                           on_click=pick_suggestion, args=(q,))


# ----------------------------------------------------------------------------- app
def main():
    render_sidebar()
    render_header()

    if not config.GROQ_API_KEY:
        st.warning(
            "**Setup needed:** add your free Groq API key to run the assistant.\n\n"
            "1. Get a key at https://console.groq.com/keys\n"
            "2. Locally: copy `.env.example` to `.env` and paste the key.\n"
            "3. On Streamlit Cloud: add `GROQ_API_KEY` in **Settings → Secrets**."
        )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Empty state: intro + suggestion chips.
    if not st.session_state.messages and not st.session_state.get("pending"):
        render_empty_state()

    # Replay history.
    for msg in st.session_state.messages:
        avatar = logo_image() if msg["role"] == "assistant" else USER_AVATAR
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            if msg.get("sources"):
                render_sources(msg["sources"])

    typed = st.chat_input("Ask me anything about intelligent infrastructure…")
    prompt = typed or st.session_state.pop("pending", None)
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=logo_image()):
        if not config.GROQ_API_KEY:
            st.error("Add your Groq API key first (see the message above).")
            st.session_state.messages.pop()
            return

        with st.spinner("Searching Dr. Jha's articles…"):
            results = rag.retrieve(prompt)
            context = rag.format_context(results)

        history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[:-1]
        ][-6:]

        try:
            answer = st.write_stream(llm.stream_answer(prompt, context, history))
        except Exception as exc:
            st.error(f"Sorry — the model call failed: {exc}")
            st.session_state.messages.pop()
            return

        render_sources(results)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": results}
    )


if __name__ == "__main__":
    main()
