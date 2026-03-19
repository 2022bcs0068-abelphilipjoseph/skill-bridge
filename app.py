import streamlit as st
import json
import os
import io
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel
from pypdf import PdfReader

# --- 0. Setup & Authentication ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- 1. Session State Initialization (THE MAGIC FIX) ---
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'quiz_question' not in st.session_state:
    st.session_state.quiz_question = None
if 'skill_progress' not in st.session_state:
    st.session_state.skill_progress = {}

# --- 2. Schemas & Helpers ---
class RoadmapItem(BaseModel):
    missing_skill: str
    timeline: str
    action_item: str
    resource_type: str 

class GapAnalysisResult(BaseModel):
    matched_skills: list[str]
    missing_skills: list[str]
    learning_roadmap: list[RoadmapItem]

@st.cache_data
def load_data():
    try:
        with open("jobs.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("⚠️ jobs.json not found. Please run generate_data.py first.")
        return {}

jobs_db = load_data()

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    return str(uploaded_file.read(), "utf-8")

# --- 3. Fallback & AI Logic ---
def fallback_analysis(user_text, target_skills):
    user_text_lower = user_text.lower()
    matched, missing = [], []
    for skill in target_skills:
        if skill.lower() in user_text_lower:
            matched.append(skill)
        else:
            missing.append(skill)
            
    fallback_roadmap = [
        {"missing_skill": s, "timeline": "1-2 Weeks", "action_item": f"Review {s} docs.", "resource_type": "Self-Study"}
        for s in missing
    ]
    return {"matched_skills": matched, "missing_skills": missing, "learning_roadmap": fallback_roadmap, "method": "Rule-Based Fallback"}

def analyze_skills_gap(user_skills_text, target_job_skills):
    if not GEMINI_API_KEY:
        return fallback_analysis(user_skills_text, target_job_skills)
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = f"""
        Analyze the candidate's text against the required job skills.
        Categorize into matched and missing. For every missing skill, create a roadmap item.
        Candidate Text: {user_skills_text}
        Required Skills: {', '.join(target_job_skills)}
        """
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite-preview',
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=GapAnalysisResult, temperature=0.2),
        )
        result = json.loads(response.text)
        result["method"] = "Gemini 3.1 Flash"
        return result
    except Exception as e:
        print(f"Error: {e}")
        return fallback_analysis(user_skills_text, target_job_skills)

# --- 4. Streamlit UI ---
st.set_page_config(page_title="Skill-Bridge Career Navigator", page_icon="🎓", layout="wide")
st.title("🎓 Skill-Bridge Career Navigator")

# Sidebar
st.sidebar.header("Target Role")
selected_role = st.sidebar.selectbox("Select a synthetic job to analyze:", list(jobs_db.keys()))
if selected_role:
    job_info = jobs_db[selected_role]
    st.sidebar.subheader("Required Skills")
    st.sidebar.write(", ".join(job_info["required_skills"]))

# Input Area
input_method = st.radio("Provide your skills:", ("Upload Resume (PDF/TXT)", "Paste Text"))
user_input = ""
if input_method == "Upload Resume (PDF/TXT)":
    uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "txt"])
    if uploaded_file: user_input = extract_text_from_file(uploaded_file)
else:
    user_input = st.text_area("Paste your skills here:", height=100)

# The Execution Button
if st.button("Run Gap Analysis 🚀"):
    if user_input.strip():
        with st.spinner("Analyzing..."):
            # SAVE TO SESSION STATE!
            st.session_state.analysis_result = analyze_skills_gap(user_input, jobs_db[selected_role]["required_skills"])
            st.session_state.quiz_question = None # Reset quiz on new analysis
            
            # Initialize Tracker State
            for skill in st.session_state.analysis_result.get("missing_skills", []):
                if skill not in st.session_state.skill_progress:
                    st.session_state.skill_progress[skill] = "Yet to Start"
    else:
        st.warning("Please provide skills first.")

# --- 5. Stateful Dashboard Rendering ---
if st.session_state.analysis_result:
    result = st.session_state.analysis_result
    st.divider()
    st.subheader(f"Dashboard: {selected_role} (Powered by {result['method']})")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ✅ Verified Skills")
        for skill in result.get("matched_skills", []): st.write(f"✔️ {skill}")
            
    with col2:
        st.markdown("### ⚠️ Missing Skills")
        for skill in result.get("missing_skills", []): st.error(f"❌ {skill}")

    # --- PERSONALIZED SKILL TRACKER ---
    if result.get("missing_skills"):
        st.divider()
        st.subheader("📈 Personal Skill Progress Tracker")
        st.write("Track your upskilling journey manually:")
        
        track_col1, track_col2 = st.columns(2)
        for i, skill in enumerate(result["missing_skills"]):
            
            target_col = track_col1 if i % 2 == 0 else track_col2
            with target_col:
                # Update session state dynamically when user changes the dropdown
                new_status = st.selectbox(
                    f"Status for **{skill}**", 
                    options=["Yet to Start", "Basic", "Skilled", "Highly Skilled"],
                    index=["Yet to Start", "Basic", "Skilled", "Highly Skilled"].index(st.session_state.skill_progress.get(skill, "Yet to Start")),
                    key=f"tracker_{skill}"
                )
                st.session_state.skill_progress[skill] = new_status

    # --- ROADMAP & EXPANDER ---
    st.divider()
    st.subheader("🗺️ Learning Roadmap")
    for item in result.get("learning_roadmap", []):
        skill_name = item.get('missing_skill', 'Unknown')
        current_status = st.session_state.skill_progress.get(skill_name, "Yet to Start")
        
        
        border_color = "green" if current_status in ["Skilled", "Highly Skilled"] else "gray"
        
        with st.container(border=True):
            st.markdown(f"**{skill_name}** - *Current Status: {current_status}*")
            st.write(f"⏱️ **Timeline:** {item.get('timeline')} | 🎯 **Action:** {item.get('action_item')}")
            with st.expander("🔗 View Recommended Resources"):
                sq = skill_name.replace(" ", "+")
                st.markdown(f"[Search {skill_name} on Coursera](https://www.coursera.org/search?query={sq})")
                st.markdown(f"[Search {skill_name} on YouTube](https://www.youtube.com/results?search_query={sq}+tutorial)")

    # --- QUIZ MASTER ---
    st.divider()
    st.subheader("🎤 Quiz Master")
    if result.get("matched_skills"):
        if st.button("Generate Interview Question 🎲"):
            with st.spinner("Drafting question..."):
                try:
                    client = genai.Client(api_key=GEMINI_API_KEY)
                    q_prompt = f"Generate ONE tough technical interview question combining these skills: {', '.join(result['matched_skills'])}."
                    response = client.models.generate_content(model='gemini-3.1-flash-lite-preview', contents=q_prompt)
                    st.session_state.quiz_question = response.text # Save to state!
                except Exception:
                    st.warning("Quiz Master AI failed. Try again.")
        
        # Display the saved question so it survives reruns
        if st.session_state.quiz_question:
            st.info(st.session_state.quiz_question)
