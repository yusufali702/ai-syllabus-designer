import streamlit as st
from langchain_community.llms import Ollama
from datetime import datetime

# =========================================
# OLLAMA MODEL
# =========================================

llm = Ollama(
    model="gemma2:2b"
)

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="AI Syllabus Designer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================
# CUSTOM CSS
# =========================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f172a, #111827, #1e293b);
    color: white;
}

/* Main Container */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Hero Section */
.hero-container {
    background: linear-gradient(
        135deg,
        rgba(79,70,229,0.25),
        rgba(147,51,234,0.25)
    );
    padding: 40px;
    border-radius: 25px;
    border: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(12px);
    margin-bottom: 25px;
    box-shadow: 0px 8px 40px rgba(0,0,0,0.4);
}

.hero-title {
    font-size: 55px;
    font-weight: 700;
    color: white;
    margin-bottom: 10px;
}

.hero-subtitle {
    font-size: 20px;
    color: #cbd5e1;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid rgba(255,255,255,0.1);
}

/* Cards */
.custom-card {
    background: rgba(255,255,255,0.05);
    border-radius: 20px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(8px);
    margin-bottom: 20px;
    box-shadow: 0px 6px 20px rgba(0,0,0,0.3);
}

/* Buttons */
.stButton > button {
    width: 100%;
    height: 60px;
    border-radius: 18px;
    border: none;
    background: linear-gradient(90deg, #4f46e5, #9333ea);
    color: white;
    font-size: 20px;
    font-weight: 600;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.02);
    background: linear-gradient(90deg, #4338ca, #7e22ce);
}

/* Generated Output */
.output-box {
    background: rgba(17,24,39,0.85);
    border-radius: 20px;
    padding: 30px;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0px 8px 30px rgba(0,0,0,0.4);
    line-height: 1.8;
}

/* Footer */
.footer {
    text-align: center;
    color: #94a3b8;
    padding-top: 20px;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# HERO SECTION
# =========================================

st.markdown("""
<div class="hero-container">

<div class="hero-title">
🚀 AI Syllabus Designer
</div>

<div class="hero-subtitle">
Generate modern, industry-ready university syllabus using AI & LLMs
</div>

</div>
""", unsafe_allow_html=True)

# =========================================
# SIDEBAR
# =========================================

st.sidebar.markdown("## ⚙️ Configuration Panel")

course_name = st.sidebar.text_input(
    "📚 Course Name",
    placeholder="Machine Learning"
)

semester = st.sidebar.selectbox(
    "🎓 Semester",
    [
        "1st Semester",
        "2nd Semester",
        "3rd Semester",
        "4th Semester",
        "5th Semester",
        "6th Semester",
        "7th Semester",
        "8th Semester"
    ]
)

difficulty = st.sidebar.selectbox(
    "📈 Difficulty Level",
    [
        "Beginner",
        "Intermediate",
        "Advanced"
    ]
)

units = st.sidebar.slider(
    "📑 Number of Units",
    1,
    10,
    5
)

technology_focus = st.sidebar.text_input(
    "💻 Technology Focus",
    placeholder="AI, Cloud Computing, Cybersecurity"
)

include_projects = st.sidebar.checkbox(
    "🚀 Include Mini Projects",
    value=True
)

include_practicals = st.sidebar.checkbox(
    "🧪 Include Practicals",
    value=True
)

# =========================================
# DASHBOARD STATS
# =========================================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="custom-card">
    <h2>⚡ AI Powered</h2>
    <p>Uses Ollama + Gemma2B</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="custom-card">
    <h2>📅 Current Date</h2>
    <p>{datetime.now().strftime('%d %B %Y')}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="custom-card">
    <h2>🎯 Smart Curriculum</h2>
    <p>Industry-Oriented Syllabus</p>
    </div>
    """, unsafe_allow_html=True)

# =========================================
# GENERATE BUTTON
# =========================================

if st.button("✨ Generate AI Syllabus"):

    if not course_name:

        st.warning("⚠️ Please enter course name")

    else:

        prompt = f"""
You are an expert syllabus designer for Indian engineering universities.

Generate a detailed syllabus.

Course Name: {course_name}
Semester: {semester}
Difficulty: {difficulty}
Technology Focus: {technology_focus}
Units: {units}

Include:

1. Course Overview
2. Course Objectives
3. Unit-wise Detailed Syllabus
4. Practical Work
5. Mini Projects
6. Learning Outcomes
7. Recommended Books
8. Software Tools
9. Industry Applications

Make the syllabus:
- Professional
- Modern
- Industry-relevant
- Properly formatted
"""

        with st.spinner("🤖 AI is generating syllabus..."):

            try:

                syllabus = llm.invoke(prompt)

                st.success("✅ Syllabus Generated Successfully!")

                # OUTPUT BOX

                st.markdown(
                    f"""
                    <div class="output-box">
                    {syllabus}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # DOWNLOAD BUTTON

                st.download_button(
                    label="📥 Download Syllabus",
                    data=syllabus,
                    file_name=f"{course_name}_syllabus.txt",
                    mime="text/plain"
                )

                # EXTRA SECTION

                st.markdown("## 🚀 Recommended Technologies")

                tech1, tech2, tech3, tech4 = st.columns(4)

                tech1.metric("AI", "Enabled")
                tech2.metric("Cloud", "Supported")
                tech3.metric("Projects", "Included")
                tech4.metric("Industry Ready", "Yes")

            except Exception as e:

                st.error(f"❌ Error: {e}")

# =========================================
# FOOTER
# =========================================

st.markdown("""
<div class="footer">

Made with ❤️ using Streamlit + Ollama + Gemma2B

</div>
""", unsafe_allow_html=True)











