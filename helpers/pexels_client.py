import random
from typing import Dict

import requests
import streamlit as st


def _placeholder(query: str, fallback_url: str) -> Dict:
    return {
        "url": fallback_url,
        "query": query,
        "attribution": None,
        "source": "placeholder",
        "credit_url": None,
    }


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_pexels_image(query: str, fallback_url: str, orientation: str = "landscape") -> Dict:
    """
    Minimal Pexels client with caching and a safe fallback.
    Returns a dict with url, attribution and source info.
    """
    api_key = st.secrets.get("PEXELS_API_KEY")
    if not api_key:
        return _placeholder(query, fallback_url)

    headers = {"Authorization": api_key}
    params = {"query": query, "per_page": 12, "orientation": orientation}

    try:
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers=headers,
            params=params,
            timeout=7,
        )
        if resp.status_code != 200:
            return _placeholder(query, fallback_url)

        data = resp.json()
        photos = data.get("photos") or []
        if not photos:
            return _placeholder(query, fallback_url)

        photo = random.choice(photos)
        src = photo.get("src") or {}
        url = (
            src.get("large2x")
            or src.get("large")
            or src.get("original")
            or src.get("medium")
        )
        if not url:
            return _placeholder(query, fallback_url)

        photographer = photo.get("photographer") or "Pexels"
        page_url = photo.get("url")
        attribution = f"Photo: {photographer} (Pexels)"

        return {
            "url": url,
            "query": query,
            "attribution": attribution,
            "source": "pexels",
            "credit_url": page_url,
        }
    except Exception:
        return _placeholder(query, fallback_url)
