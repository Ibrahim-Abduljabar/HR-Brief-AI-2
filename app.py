import streamlit as st
import pdfplumber
import requests
import re
from logsnag import LogSnag

log_client = LogSnag(token=st.secrets["LOGSNAG_TOKEN"], project="hr-brief-ai")
log_client.track(channel="visits", event="New Visit")
API_KEY = st.secrets["API_BBB"]

def detect_language(text):
    if re.search(r'[\u0600-\u06FF]', text):
        return "arabic"
    return "english"

def summarize_text(text):
    lang = detect_language(text)

    system_msg = "Summarize the following text in English only."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": text}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    result = response.json()

    return result["choices"][0]["message"]["content"]


st.set_page_config(page_title="HR Brief AI", layout="wide")

st.title("HR Brief AI")
st.write("### AI-Powered HR Report Summarization Tool")


st.write("#### Report No. 1")
file1 = st.file_uploader("Upload the first PDF report here", type=["pdf"], key="pdf1")

if file1:
    with pdfplumber.open(file1) as pdf:
        text = ""
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"

    summary1 = summarize_text(text)
    st.write("## Summary of Report No. 1")
    st.write(summary1)

st.write("---")


if "reports" not in st.session_state:
    st.session_state["reports"] = []

for i, report in enumerate(st.session_state["reports"]):
    st.write(f"#### Report No. {i+2}")

    file2 = st.file_uploader(
        "Upload PDF report here",
        type=["pdf"],
        key=f"pdf_new_{i}"
    )

    if file2 and not report.get("uploaded", False):
        with pdfplumber.open(file2) as pdf:
            text2 = ""
            for page in pdf.pages:
                t2 = page.extract_text()
                if t2:
                    text2 += t2 + "\n"

        summary2 = summarize_text(text2)
        report["uploaded"] = True
        report["summary"] = summary2

    if report.get("uploaded", False):
        st.write(f"## Summary of Report No. {i+2}")
        st.write(report["summary"])

    st.write("---")

if st.button("Summarize Another Report"):
    st.session_state["reports"].append({"uploaded": False})

st.write("### If you want to print the summary as a PDF, press Ctrl + P (or Cmd + P on Mac)")
