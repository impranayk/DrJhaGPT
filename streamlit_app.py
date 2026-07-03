"""Dr. Pranay Jha AI Assistant — a Streamlit chatbot.

Open-source stack: Groq (open LLMs) for generation + retrieval over
drpranayjha.com content. No IBM / HCL dependencies.
"""
import streamlit as st

from chatbot import config, llm, rag

st.set_page_config(
    page_title=config.BRAND_NAME,
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- Brand polish on top of the .streamlit/config.toml theme ---
st.markdown(
    """
    <style>
      .block-container { padding-top: 2.5rem; max-width: 820px; }
      .brand-title { font-size: 1.9rem; font-weight: 800; letter-spacing: -0.5px;
                     margin-bottom: 0; }
      .brand-title span { color: #E11D2A; }
      .brand-tagline { color: #9AA4B8; font-size: 0.95rem; margin-top: 0.15rem; }
      .source-pill { display:inline-block; background:#151C2E; border:1px solid #263049;
                     color:#C7D0E0; padding:2px 10px; border-radius:999px;
                     font-size:0.78rem; margin:3px 4px 0 0; text-decoration:none; }
      .source-pill:hover { border-color:#E11D2A; }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_header():
    st.markdown(
        f'<div class="brand-title">DrJha<span>GPT</span></div>'
        f'<div class="brand-tagline">{config.BRAND_TAGLINE}</div>',
        unsafe_allow_html=True,
    )
    st.write("")


def render_sidebar():
    with st.sidebar:
        st.markdown(f"### {config.BRAND_NAME}")
        st.caption("Ask me about VMware, cloud, datacenters & AI — answers drawn "
                   "from Dr. Jha's published work.")
        st.markdown(f"🌐 [drpranayjha.com]({config.WEBSITE_URL})")
        st.divider()
        st.caption(f"Model: `{config.GROQ_MODEL}` (via Groq)")
        kb = "✅ loaded" if rag.has_knowledge() else "⚠️ not built yet"
        st.caption(f"Knowledge base: {kb}")
        if st.button("🧹 Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


def render_sources(results):
    if not results:
        return
    # De-duplicate by article link while preserving order.
    seen, pills = set(), []
    for r in results:
        link, title = r.get("url"), r.get("title", "Article")
        if link and link not in seen:
            seen.add(link)
            pills.append(f'<a class="source-pill" href="{link}" target="_blank">📄 {title}</a>')
    if pills:
        st.markdown("**Sources:** " + " ".join(pills), unsafe_allow_html=True)


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

    # Replay history.
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                render_sources(msg["sources"])

    prompt = st.chat_input("Ask me anything about intelligent infrastructure…")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not config.GROQ_API_KEY:
            st.error("Add your Groq API key first (see the message above).")
            st.session_state.messages.pop()  # don't keep an unanswered turn
            return

        # Retrieve grounding context from Dr. Jha's content.
        results = rag.retrieve(prompt)
        context = rag.format_context(results)

        # Only the last several turns are sent back as conversation history.
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[:-1]
        ][-6:]

        try:
            answer = st.write_stream(llm.stream_answer(prompt, context, history))
        except Exception as exc:  # surface a clean message, log detail server-side
            st.error(f"Sorry — the model call failed: {exc}")
            st.session_state.messages.pop()
            return

        render_sources(results)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": results}
    )


if __name__ == "__main__":
    main()
