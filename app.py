import streamlit as st
from langchain_community.llms import Ollama
from datetime import datetime
import PyPDF2
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import tempfile
import json
import re

# =========================================
# OLLAMA MODEL
# =========================================

@st.cache_resource
def load_llm():
    return Ollama(model="gemma2:2b")

llm = load_llm()

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="AI Syllabus Designer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================
# CUSTOM CSS — Refined Dark Editorial Theme
# =========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ---- GLOBAL BG ---- */
.stApp {
    background-color: #0c0f14;
    color: #e8e3d9;
}

.main .block-container {
    padding: 2rem 2.5rem 4rem;
    max-width: 1200px;
}

/* ---- SIDEBAR ---- */
[data-testid="stSidebar"] {
    background: #0f1318;
    border-right: 1px solid rgba(255,255,255,0.07);
}
[data-testid="stSidebar"] * {
    color: #c9c4bb !important;
}
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stSelectbox select,
[data-testid="stSidebar"] .stTextArea textarea {
    background: #161b22 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #e8e3d9 !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] label {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #9a9490 !important;
    letter-spacing: 0.04em;
}

/* ---- HERO ---- */
.hero-wrap {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 36px;
    padding-bottom: 28px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
.hero-eyebrow {
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #a78e6a;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 52px;
    font-weight: 400;
    line-height: 1.1;
    color: #f0ebe2;
    margin: 0;
}
.hero-title em {
    font-style: italic;
    color: #c4a87a;
}
.hero-sub {
    font-size: 16px;
    font-weight: 300;
    color: #7a7571;
    max-width: 540px;
    line-height: 1.6;
}

/* ---- STAT CARDS ---- */
.stat-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 32px;
}
.stat-card {
    background: #131720;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 16px 20px;
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #a78e6a, transparent);
}
.stat-label {
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #5a5650;
    margin-bottom: 6px;
}
.stat-value {
    font-family: 'DM Serif Display', serif;
    font-size: 22px;
    color: #e8e3d9;
}
.stat-sub {
    font-size: 12px;
    color: #5a5650;
    margin-top: 2px;
}

/* ---- SECTION HEADERS ---- */
.section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 22px;
    color: #f0ebe2;
    margin-bottom: 4px;
}
.section-line {
    height: 1px;
    background: rgba(255,255,255,0.07);
    margin-bottom: 20px;
}

/* ---- TAB-LIKE MODE TOGGLE ---- */
.mode-tabs {
    display: flex;
    gap: 8px;
    margin-bottom: 24px;
}
.mode-tab {
    padding: 8px 20px;
    border-radius: 100px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    border: 1px solid rgba(255,255,255,0.1);
    color: #7a7571;
    background: transparent;
    transition: all 0.2s;
}
.mode-tab.active {
    background: #a78e6a;
    border-color: #a78e6a;
    color: #0c0f14;
}

/* ---- FORM INPUTS ---- */
.stTextInput input, .stTextArea textarea,
.stNumberInput input {
    background: #131720 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: #e8e3d9 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: rgba(167, 142, 106, 0.5) !important;
    box-shadow: 0 0 0 3px rgba(167,142,106,0.1) !important;
}
.stSelectbox [data-baseweb="select"] {
    background: #131720 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
}
.stSelectbox span {
    color: #e8e3d9 !important;
}
label {
    color: #9a9490 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
}
.stSlider > div > div > div {
    background: #a78e6a !important;
}

/* ---- MAIN GENERATE BUTTON ---- */
.stButton > button {
    background: #a78e6a;
    color: #0c0f14;
    border: none;
    border-radius: 12px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 15px;
    letter-spacing: 0.02em;
    padding: 14px 32px;
    width: 100%;
    transition: all 0.25s;
}
.stButton > button:hover {
    background: #c4a87a;
    transform: translateY(-1px);
}
.stButton > button:active {
    transform: translateY(0);
}

/* ---- PROGRESS BAR ---- */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #a78e6a, #c4a87a) !important;
}

/* ---- OUTPUT BOX ---- */
.output-wrap {
    background: #0f1318;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    overflow: hidden;
}
.output-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 24px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    background: rgba(255,255,255,0.02);
}
.output-title {
    font-family: 'DM Serif Display', serif;
    font-size: 16px;
    color: #c4a87a;
}
.output-body {
    padding: 28px;
    line-height: 1.85;
    color: #c9c4bb;
    font-size: 14.5px;
    white-space: pre-wrap;
    font-family: 'DM Sans', sans-serif;
}

/* ---- UNIT CARDS in output ---- */
.unit-card {
    background: rgba(167,142,106,0.06);
    border: 1px solid rgba(167,142,106,0.15);
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 16px;
}
.unit-number {
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #a78e6a;
    margin-bottom: 4px;
}
.unit-title {
    font-family: 'DM Serif Display', serif;
    font-size: 18px;
    color: #f0ebe2;
}

/* ---- METRICS ROW ---- */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-top: 24px;
}
.metric-pill {
    background: #131720;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 12px 16px;
    text-align: center;
}
.metric-icon { font-size: 20px; }
.metric-label { font-size: 11px; color: #5a5650; margin-top: 4px; letter-spacing: 0.06em; text-transform: uppercase; }
.metric-val { font-weight: 600; color: #a78e6a; font-size: 13px; }

/* ---- INFO BOX ---- */
.info-box {
    background: rgba(167,142,106,0.08);
    border: 1px solid rgba(167,142,106,0.2);
    border-radius: 12px;
    padding: 14px 18px;
    font-size: 13px;
    color: #c4a87a;
    margin-bottom: 20px;
}

/* ---- DOWNLOAD BUTTONS ---- */
.stDownloadButton > button {
    background: transparent;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px;
    color: #c9c4bb;
    font-size: 14px;
    font-weight: 500;
    width: 100%;
    padding: 10px;
    transition: all 0.2s;
}
.stDownloadButton > button:hover {
    border-color: #a78e6a;
    color: #a78e6a;
    background: rgba(167,142,106,0.06);
}

/* ---- SUCCESS/ERROR ---- */
.stSuccess {
    background: rgba(39, 80, 10, 0.3) !important;
    border: 1px solid rgba(99,153,34,0.3) !important;
    border-radius: 10px !important;
}
.stAlert {
    border-radius: 10px !important;
}

/* ---- EXPANDER ---- */
.streamlit-expanderHeader {
    background: #131720 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: #c9c4bb !important;
}

/* ---- RADIO ---- */
.stRadio label {
    font-size: 14px !important;
    color: #c9c4bb !important;
}

/* ---- CHECKBOX ---- */
.stCheckbox label {
    color: #9a9490 !important;
    font-size: 13px !important;
}

/* Footer */
.footer-bar {
    border-top: 1px solid rgba(255,255,255,0.06);
    padding-top: 24px;
    margin-top: 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: #3a3733;
    font-size: 12px;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# SESSION STATE INIT
# =========================================

if "syllabus_output" not in st.session_state:
    st.session_state.syllabus_output = None
if "generation_count" not in st.session_state:
    st.session_state.generation_count = 0
if "last_course" not in st.session_state:
    st.session_state.last_course = ""
if "history" not in st.session_state:
    st.session_state.history = []

# =========================================
# HERO
# =========================================

st.markdown("""
<div class="hero-wrap">
    <div class="hero-eyebrow">AI-Powered Academic Tool</div>
    <h1 class="hero-title">Syllabus <em>Designer</em></h1>
    <p class="hero-sub">Generate and upgrade university syllabi using local LLMs. Industry-aligned, outcome-driven, ready to publish.</p>
</div>
""", unsafe_allow_html=True)

# =========================================
# STAT CARDS
# =========================================

st.markdown(f"""
<div class="stat-row">
    <div class="stat-card">
        <div class="stat-label">Engine</div>
        <div class="stat-value">Ollama</div>
        <div class="stat-sub">Gemma 2B · Local</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Session</div>
        <div class="stat-value">{st.session_state.generation_count}</div>
        <div class="stat-sub">syllabi generated</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Date</div>
        <div class="stat-value">{datetime.now().strftime('%d %b')}</div>
        <div class="stat-sub">{datetime.now().strftime('%Y')}</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Output</div>
        <div class="stat-value">PDF + TXT</div>
        <div class="stat-sub">Export ready</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================
# SIDEBAR — CONFIGURATION
# =========================================

with st.sidebar:
    st.markdown("### Configuration")

    mode = st.radio(
        "Mode",
        ["✨ Generate New Syllabus", "🔄 Upgrade Existing Syllabus"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**🏫 Institution Details**")

    college_name = st.text_input("College / University", "XYZ Institute of Technology")
    branch = st.text_input("Branch / Department", "Computer Science Engineering")

    col_s, col_y = st.columns(2)
    with col_s:
        semester = st.selectbox("Semester", [f"{i}{'st' if i==1 else 'nd' if i==2 else 'rd' if i==3 else 'th'} Sem" for i in range(1, 9)])
    with col_y:
        year = st.text_input("Academic Year", "2026-27")

    st.markdown("---")
    st.markdown("**📚 Course Details**")

    course_name = st.text_input("Course Name", placeholder="e.g., Machine Learning")
    course_code = st.text_input("Course Code", placeholder="e.g., CS601")

    col_c, col_d = st.columns(2)
    with col_c:
        credits = st.number_input("Credits", min_value=1, max_value=6, value=4)
    with col_d:
        difficulty = st.selectbox("Level", ["Beginner", "Intermediate", "Advanced"])

    units = st.slider("Number of Units", 1, 10, 5)
    hours_per_week = st.slider("Hrs/Week (Lecture)", 1, 6, 3)

    technology_focus = st.text_input("Technology Focus", placeholder="AI, Cloud, Cybersecurity")

    st.markdown("---")
    st.markdown("**⚙️ Advanced Options**")

    include_practicals = st.checkbox("Include Practicals / Lab Work", value=True)
    include_references = st.checkbox("Include Reference Books", value=True)
    include_outcomes = st.checkbox("Include Course Outcomes (COs)", value=True)
    include_mapping = st.checkbox("Include CO–PO Mapping Table", value=False)

    exam_pattern = st.selectbox(
        "Exam Pattern",
        ["Mid-Term + End-Term", "Continuous Assessment", "Project-Based", "Quarterly"]
    )

    st.markdown("---")

    # PDF Upload (Upgrade mode)
    uploaded_pdf = None
    if "Upgrade" in mode:
        st.markdown("**📄 Upload Existing Syllabus**")
        uploaded_pdf = st.file_uploader("PDF only", type=["pdf"])

    # History in sidebar
    if st.session_state.history:
        st.markdown("---")
        st.markdown("**🕘 Recent Generations**")
        for h in reversed(st.session_state.history[-5:]):
            st.markdown(f"<small style='color:#5a5650'>• {h}</small>", unsafe_allow_html=True)

# =========================================
# MAIN AREA — TWO COLUMNS
# =========================================

left_col, right_col = st.columns([1.2, 1], gap="large")

with left_col:

    st.markdown('<div class="section-header">Build Your Syllabus</div><div class="section-line"></div>', unsafe_allow_html=True)

    # Optional course description
    course_desc = st.text_area(
        "Course Description (optional)",
        placeholder="Brief context about the course, prerequisites, or special instructions for the AI...",
        height=90
    )

    # Quick Presets
    st.markdown("**Quick Presets**")
    preset_cols = st.columns(4)
    presets = {
        "🤖 ML / AI": {"course": "Machine Learning", "tech": "TensorFlow, PyTorch, LLMs"},
        "☁️ Cloud": {"course": "Cloud Computing", "tech": "AWS, Azure, Kubernetes"},
        "🔒 Security": {"course": "Cybersecurity", "tech": "Ethical Hacking, SIEM, Zero Trust"},
        "📊 Data": {"course": "Data Science", "tech": "Python, SQL, Tableau, Spark"},
    }
    for i, (label, vals) in enumerate(presets.items()):
        with preset_cols[i]:
            if st.button(label, key=f"preset_{i}"):
                st.session_state["_preset_course"] = vals["course"]
                st.session_state["_preset_tech"] = vals["tech"]
                st.rerun()

    # Apply preset values if set
    if "_preset_course" in st.session_state:
        st.info(f"✓ Preset loaded: **{st.session_state['_preset_course']}** — update the sidebar fields to match.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Generate Button
    generate_btn = st.button("✦ Generate AI Syllabus", use_container_width=True)

    # Info box
    st.markdown("""
    <div class="info-box">
    💡 All generation runs locally via Ollama. No data leaves your machine.
    </div>
    """, unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="section-header">Live Preview</div><div class="section-line"></div>', unsafe_allow_html=True)

    if st.session_state.syllabus_output:
        # Show first 600 chars as preview
        preview = st.session_state.syllabus_output[:700] + "\n\n[... scroll down for full output]"
        st.markdown(f"""
        <div class="output-wrap">
            <div class="output-header">
                <span class="output-title">📄 {st.session_state.last_course}</span>
                <span style="font-size:12px;color:#5a5650">{datetime.now().strftime('%H:%M')}</span>
            </div>
            <div class="output-body">{preview}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="output-wrap" style="min-height:260px;display:flex;align-items:center;justify-content:center;">
            <div style="text-align:center;color:#3a3733">
                <div style="font-size:36px;margin-bottom:10px">📋</div>
                <div style="font-size:14px">Your syllabus preview will appear here</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =========================================
# PDF TEXT EXTRACTION
# =========================================

def extract_pdf_text(pdf_file):
    text = ""
    reader = PyPDF2.PdfReader(pdf_file)
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

# =========================================
# ENHANCED PDF GENERATION
# =========================================

def create_pdf(content, course_name, college_name, branch, semester, year, units, technology_focus, credits, course_code, exam_pattern):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(
        tmp.name,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2.2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        fontName='Helvetica-Bold',
        spaceAfter=4,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1a1a1a')
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica',
        spaceAfter=2,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#555555')
    )
    heading2_style = ParagraphStyle(
        'H2Custom',
        parent=styles['Heading2'],
        fontSize=13,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#2c3e50'),
        spaceBefore=14,
        spaceAfter=6,
        borderPad=(0, 0, 4, 0)
    )
    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['BodyText'],
        fontSize=10,
        fontName='Helvetica',
        leading=15,
        spaceAfter=4,
        textColor=colors.HexColor('#2d2d2d')
    )

    elements = []

    # ---- Header Bar (simulated via table) ----
    header_table = Table(
        [[Paragraph(college_name, title_style)]],
        colWidths=[17*cm]
    )
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f5f1eb')),
        ('TOPPADDING', (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
        ('LINEBELOW', (0,0), (-1,-1), 2, colors.HexColor('#a78e6a')),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 12))

    # ---- Info Table ----
    info_data = [
        [
            Paragraph(f"<b>Branch:</b> {branch}", body_style),
            Paragraph(f"<b>Semester:</b> {semester}", body_style),
            Paragraph(f"<b>Academic Year:</b> {year}", body_style),
        ],
        [
            Paragraph(f"<b>Course Code:</b> {course_code or 'N/A'}", body_style),
            Paragraph(f"<b>Credits:</b> {credits}", body_style),
            Paragraph(f"<b>Exam Pattern:</b> {exam_pattern}", body_style),
        ]
    ]
    info_table = Table(info_data, colWidths=[5.8*cm, 5.4*cm, 5.8*cm])
    info_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#fafaf8')),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 18))

    # ---- Course Title ----
    elements.append(Paragraph(f"Course: {course_name}", title_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0d8cc'), spaceAfter=16))

    # ---- Syllabus Body ----
    for line in content.split("\n"):
        stripped = line.strip()
        if not stripped:
            elements.append(Spacer(1, 5))
            continue

        if re.match(r'^UNIT\s+\d+', stripped, re.IGNORECASE):
            elements.append(Spacer(1, 10))
            unit_para = Paragraph(stripped, heading2_style)
            unit_box = Table([[unit_para]], colWidths=[17*cm])
            unit_box.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f5f1eb')),
                ('LINEBELOW', (0,0), (-1,-1), 1.5, colors.HexColor('#a78e6a')),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 12),
            ]))
            elements.append(unit_box)
        elif stripped.startswith("**") or stripped.startswith("##"):
            clean = stripped.replace("**", "").replace("##", "").strip()
            elements.append(Paragraph(f"<b>{clean}</b>", heading2_style))
        elif re.match(r'^\d+\.', stripped):
            elements.append(Paragraph(f"&nbsp;&nbsp;{stripped}", body_style))
        else:
            elements.append(Paragraph(stripped, body_style))
        elements.append(Spacer(1, 3))

    # ---- Summary Table ----
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Summary", heading2_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#dddddd'), spaceAfter=10))

    summary_data = [
        [Paragraph(h, ParagraphStyle('th', parent=body_style, fontName='Helvetica-Bold')) for h in
         ["Course", "Code", "Semester", "Credits", "Units", "Focus"]],
        [Paragraph(str(v), body_style) for v in
         [course_name, course_code or "—", semester, str(credits), str(units), technology_focus or "—"]]
    ]
    summary_table = Table(summary_data, colWidths=[3.5*cm, 2.2*cm, 2.2*cm, 2*cm, 2*cm, 5.1*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#fafaf8')]),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ]))
    elements.append(summary_table)

    doc.build(elements)
    return tmp.name

# =========================================
# PROMPT BUILDER
# =========================================

def build_prompt(mode_is_upgrade, existing_text=""):
    extras = []
    if include_practicals:
        extras.append("- Include minimum 10 descriptive practical/lab experiments after all units")
    if include_references:
        extras.append("- Include 5-8 reference books (Author, Title, Publisher, Year)")
    if include_outcomes:
        extras.append("- Include 5 Course Outcomes (COs) at the start")
    if include_mapping:
        extras.append("- Add a CO-PO mapping table at the end (COs vs PO1..PO12)")

    extras_str = "\n".join(extras) if extras else "(standard format)"
    exam_info = f"Exam Pattern: {exam_pattern}"
    desc_info = f"Course Description: {course_desc}" if course_desc else ""

    base = f"""
College: {college_name}
Branch: {branch}
Semester: {semester} | Academic Year: {year}
Course: {course_name} | Code: {course_code or 'N/A'} | Credits: {credits}
Difficulty: {difficulty} | Hours/Week: {hours_per_week}
Technology Focus: {technology_focus}
Number of Units: {units}
{exam_info}
{desc_info}

Extra Requirements:
{extras_str}
"""

    if mode_is_upgrade:
        return f"""
Analyze the following existing syllabus and generate a MODERNIZED, UPGRADED version.

{base}

--- EXISTING SYLLABUS ---
{existing_text}
--- END ---

YOUR TASK:
- Keep the core structure but upgrade outdated topics
- Add latest industry-relevant technologies and tools
- Integrate AI/ML applications where relevant
- Improve teaching-learning outcomes
- Ensure each unit has: title, topics, teaching hours, expected outcomes

FORMAT:
1. Start with COURSE OUTCOMES (if requested)
2. UNIT 1 through UNIT {units} — descriptive academic content, no bullet spam
3. Teaching hours per unit (total ≈ {hours_per_week * 16} hrs/semester)
4. Practicals (if requested)
5. References (if requested)
6. SUMMARY TABLE at end: | Unit | Unit Name | Hours | Key Topics |

Keep it professional, industry-oriented, and future-ready.
"""
    else:
        return f"""
Generate a complete, professional university syllabus.

{base}

FORMAT RULES:
1. Start with COURSE OUTCOMES (if requested)
2. UNIT 1 through UNIT {units}
   - Unit title
   - Descriptive topic content (NOT bullet points — use academic prose)
   - Teaching Hours
   - Expected Learning Outcomes
   - Industry Applications
3. Experiments / Practicals section (if requested)
4. Reference Books (if requested)
5. End with SUMMARY TABLE: | Unit | Unit Name | Hours | Experiments |

IMPORTANT:
- Total hours ≈ {hours_per_week * 16} hrs/semester spread across units
- Use latest {datetime.now().year} technologies
- Keep content university-standard and industry-aligned
- Avoid outdated frameworks or deprecated tools
"""

# =========================================
# GENERATION LOGIC
# =========================================

if generate_btn:
    if not course_name.strip():
        st.warning("⚠️ Please enter a course name in the sidebar.")
    else:
        existing_text = ""
        if "Upgrade" in mode and uploaded_pdf:
            try:
                existing_text = extract_pdf_text(uploaded_pdf)
            except Exception as e:
                st.error(f"❌ PDF read error: {e}")

        mode_is_upgrade = "Upgrade" in mode
        prompt = build_prompt(mode_is_upgrade, existing_text)

        st.markdown("---")
        st.markdown("### Generating Syllabus...")
        progress = st.progress(0, text="Starting AI engine...")

        try:
            # Streaming generation with progress simulation
            progress.progress(15, text="Warming up model...")

            with st.spinner(""):
                progress.progress(35, text="Generating unit content...")
                syllabus = llm.invoke(prompt)
                progress.progress(80, text="Formatting output...")

            progress.progress(100, text="Done!")
            st.session_state.syllabus_output = syllabus
            st.session_state.last_course = course_name
            st.session_state.generation_count += 1
            timestamp = datetime.now().strftime('%H:%M')
            st.session_state.history.append(f"{course_name} ({timestamp})")

            st.success("✅ Syllabus generated successfully!")

            # ---- Full Output Display ----
            st.markdown(f"""
            <div class="output-wrap">
                <div class="output-header">
                    <span class="output-title">📄 {course_name} — {semester} · {year}</span>
                    <span style="font-size:12px;color:#5a5650">{college_name}</span>
                </div>
                <div class="output-body">{syllabus}</div>
            </div>
            """, unsafe_allow_html=True)

            # ---- Metrics ----
            word_count = len(syllabus.split())
            unit_count = len(re.findall(r'UNIT\s+\d+', syllabus, re.IGNORECASE))
            exp_count = len(re.findall(r'\d+\.', syllabus))

            st.markdown(f"""
            <div class="metrics-row">
                <div class="metric-pill">
                    <div class="metric-val">{word_count:,}</div>
                    <div class="metric-label">Words</div>
                </div>
                <div class="metric-pill">
                    <div class="metric-val">{unit_count}</div>
                    <div class="metric-label">Units Detected</div>
                </div>
                <div class="metric-pill">
                    <div class="metric-val">{exp_count}</div>
                    <div class="metric-label">Numbered Items</div>
                </div>
                <div class="metric-pill">
                    <div class="metric-val">{credits} Cr</div>
                    <div class="metric-label">Credits</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ---- Downloads ----
            st.markdown("---")
            st.markdown("### Download Output")

            dl_col1, dl_col2, dl_col3 = st.columns(3)

            with dl_col1:
                st.download_button(
                    "📥 Download TXT",
                    data=syllabus,
                    file_name=f"{course_name.replace(' ','_')}_syllabus.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            with dl_col2:
                pdf_path = create_pdf(
                    syllabus, course_name, college_name, branch,
                    semester, year, units, technology_focus,
                    credits, course_code, exam_pattern
                )
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        "📄 Download PDF",
                        data=pdf_file,
                        file_name=f"{course_name.replace(' ','_')}_syllabus.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

            with dl_col3:
                json_export = json.dumps({
                    "college": college_name,
                    "branch": branch,
                    "semester": semester,
                    "year": year,
                    "course": course_name,
                    "code": course_code,
                    "credits": credits,
                    "difficulty": difficulty,
                    "units": units,
                    "technology_focus": technology_focus,
                    "exam_pattern": exam_pattern,
                    "generated_at": datetime.now().isoformat(),
                    "syllabus": syllabus
                }, indent=2)
                st.download_button(
                    "🗂 Download JSON",
                    data=json_export,
                    file_name=f"{course_name.replace(' ','_')}_syllabus.json",
                    mime="application/json",
                    use_container_width=True
                )

            # ---- Expandable raw text ----
            with st.expander("📋 View Raw Text"):
                st.code(syllabus, language=None)

        except Exception as e:
            progress.empty()
            st.error(f"❌ Generation failed: {e}")
            st.info("Make sure Ollama is running locally: `ollama serve` and model is pulled: `ollama pull gemma2:2b`")

# =========================================
# FOOTER
# =========================================

st.markdown("""
<div class="footer-bar">
    <span>AI Syllabus Designer · Powered by Ollama + Gemma 2B · Runs 100% locally</span>
    <span>Built with Streamlit</span>
</div>
""", unsafe_allow_html=True)