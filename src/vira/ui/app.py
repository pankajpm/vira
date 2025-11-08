"""Streamlit prototype for interacting with the Iteration 1 backend."""

from __future__ import annotations

import io
from pathlib import Path

import httpx
import streamlit as st

from vira.business_plan.parser import SUPPORTED_EXTENSIONS, UnsupportedFormatError
from vira.config.settings import get_settings


def _post_analyze_text(client: httpx.Client, url: str, company: str, text: str) -> dict:
    response = client.post(
        f"{url}/analyze",
        json={"company_name": company, "plan_text": text},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def _post_analyze_file(client: httpx.Client, url: str, company: str, filename: str, data: bytes) -> dict:
    files = {"file": (filename, data)}
    response = client.post(
        f"{url}/analyze/upload",
        params={"company_name": company},
        files=files,
        timeout=90,
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    st.set_page_config(page_title="VIRA Alignment Checker", page_icon="🤖", layout="wide")
    st.title("VIRA Iteration 1 – a16z Alignment Checker")

    settings = get_settings()
    api_url = str(settings.streamlit_backend_url or "http://localhost:8000").rstrip("/")

    st.sidebar.header("Configuration")
    st.sidebar.write(f"Backend: {api_url}")

    company = st.text_input("Company Name", placeholder="Acme Robotics")
    plan_text = st.text_area(
        "Business Plan",
        height=300,
        placeholder="Paste core sections of your plan (problem, solution, market, team, traction)...",
    )
    uploaded_file = st.file_uploader("Or upload a PDF/DOCX/TXT", type=[ext[1:] for ext in SUPPORTED_EXTENSIONS])

    analyze_clicked = st.button("Analyze Alignment", type="primary")

    if analyze_clicked:
        if not company:
            st.error("Please provide a company name.")
            return

        if not plan_text and not uploaded_file:
            st.error("Provide plan text or upload a document to analyze.")
            return

        with httpx.Client() as client:
            try:
                if uploaded_file is not None:
                    data = uploaded_file.read()
                    result = _post_analyze_file(client, api_url, company, uploaded_file.name, data)
                else:
                    result = _post_analyze_text(client, api_url, company, plan_text)
            except httpx.HTTPStatusError as exc:
                st.error(f"Request failed with status {exc.response.status_code}: {exc.response.text}")
                st.info(f"Attempted URL: {exc.request.url}")
                return
            except httpx.HTTPError as exc:
                st.error(f"Request failed: {exc}")
                st.info(f"Backend URL: {api_url}")
                return
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")
                return

        st.markdown("---")
        st.subheader(f"Alignment Analysis – {result['company_name']}")
        st.caption(f"Generated with model {result['model_name']} (context docs: {result['retrieved_documents']})")

        cols = st.columns(2)
        with cols[0]:
            st.markdown("### Alignment Strengths")
            for item in result.get("aligns", []):
                st.markdown(f"**{item['title']}**")
                st.write(item["explanation"])
                for source in item.get("sources", []):
                    st.caption(source)

        with cols[1]:
            st.markdown("### Alignment Gaps")
            for item in result.get("gaps", []):
                st.markdown(f"**{item['title']}**")
                st.write(item["explanation"])
                for source in item.get("sources", []):
                    st.caption(source)

        st.markdown("### Summary")
        st.write(result.get("summary", ""))


if __name__ == "__main__":
    main()

