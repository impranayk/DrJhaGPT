"""Central configuration for the Dr. Pranay Jha AI Assistant.

Reads settings from environment variables (loaded from a local .env in
development, or from Streamlit secrets when deployed to Streamlit Cloud).
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load a local .env if present (no-op in production where env vars are set).
load_dotenv()

# --- Paths ---
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
EMBEDDINGS_PATH = DATA_DIR / "knowledge.npz"      # numpy vectors
CHUNKS_PATH = DATA_DIR / "chunks.json"            # text + metadata


def _get(name: str, default: str = "") -> str:
    """Read a setting from env first, then Streamlit secrets if available."""
    value = os.getenv(name)
    if value:
        return value
    try:  # Streamlit secrets are optional and only exist when deployed.
        import streamlit as st

        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return default


# --- LLM (Groq) ---
GROQ_API_KEY = _get("GROQ_API_KEY")
GROQ_MODEL = _get("GROQ_MODEL", "llama-3.3-70b-versatile")

# --- Retrieval / RAG ---
EMBED_MODEL = _get("EMBED_MODEL", "BAAI/bge-small-en-v1.5")
RAG_TOP_K = int(_get("RAG_TOP_K", "4"))
RAG_MIN_SCORE = float(_get("RAG_MIN_SCORE", "0.30"))

# --- Branding ---
BRAND_NAME = "DrJhaGPT"
BRAND_TAGLINE = "GenAI for Intelligent Infrastructure"
WEBSITE_URL = "https://drpranayjha.com"
