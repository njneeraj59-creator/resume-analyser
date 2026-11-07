import streamlit as st
from pypdf import PdfReader
from analyzer import analyze


def read_pdf(file) -> str:
    return "\n".join(p.extract_text() or "" for p in PdfReader(file).pages)


def show_list(title, items):
    st.subheader(title)
    for i in items:
        st.write(f"- {i}")


st.set_page_config(page_title="Resume Analyzer", page_icon="📄", layout="wide")
st.title("📄 Resume Analyzer")
st.caption("Runs fully on your computer. No API key needed.")

c1, c2 = st.columns(2)
with c1:
    st.subheader("Your resume")
    up = st.file_uploader("Upload PDF", type=["pdf"])
    resume = st.text_area("...or paste resume text", height=250)
    if up is not None:
        resume = read_pdf(up)
        st.success(f"Read {len(resume)} characters from the PDF.")
with c2:
    st.subheader("Job description")
    job = st.text_area("Paste the job description", height=330)

if st.button("Analyze", type="primary"):
    if not resume.strip() or not job.strip():
        st.error("Please provide both a resume and a job description.")
    else:
        r = analyze(resume, job)
        st.divider()
        st.metric("Match score", f"{r['match_score']}%")
        st.progress(min(max(r["match_score"], 0), 100) / 100)
        st.info(r["summary"])
        a, b = st.columns(2)
        with a:
            show_list("✅ Matching skills", r["matching_skills"] or ["None detected"])
            show_list("💪 Strengths", r["strengths"])
        with b:
            show_list("❌ Missing skills", r["missing_skills"] or ["None"])
            show_list("🛠️ Suggested improvements", r["improvements"])
        st.subheader("✍️ Suggested summary")
        st.write(r["improved_summary"])
