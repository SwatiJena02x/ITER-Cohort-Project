import streamlit as st
import pandas as pd
import time
import os

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="ProctorIQ",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom CSS Theme (Plus Jakarta Sans, Gradients & Clean Cards)
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f0f4fd 0%, #f7f9fe 50%, #f2edfe 100%);
        color: #1e293b;
    }
    
    /* Primary Cards */
    .portal-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 28px;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.08), 0 8px 10px -6px rgba(59, 130, 246, 0.04);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    
    /* Feature Badge Cards */
    .feature-card {
        background: #ffffff;
        border: 1px solid #e0e7ff;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
    }
    
    /* Headers & Subtext */
    .main-title {
        color: #0f172a;
        font-weight: 800;
        font-size: 2.2rem;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
    }
    
    .gradient-subtitle {
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 1.3rem;
        margin-bottom: 16px;
    }

    /* Action Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #2563eb 0%, #6366f1 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.4rem !important;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
    }
    
    /* Stats & Metric Box */
    .stat-box {
        background: white;
        border-radius: 14px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        text-align: left;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 800;
        color: #0f172a;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
    }
    
    /* Risk Badges */
    .risk-high {
        color: #ef4444;
        background: #fee2e2;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    
    .risk-medium {
        color: #f59e0b;
        background: #fef3c7;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }

    .risk-low {
        color: #10b981;
        background: #d1fae5;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    
    /* Sidebar Navigation Customization */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: #cbd5e1;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# State Management
# ---------------------------------------------------------
if 'auth_status' not in st.session_state:
    st.session_state.auth_status = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None  # 'Admin' or 'Student'
if 'page' not in st.session_state:
    st.session_state.page = 'login'  # 'login' or 'register'
if 'active_nav' not in st.session_state:
    st.session_state.active_nav = 'Dashboard'
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Mock database
if 'students_db' not in st.session_state:
    st.session_state.students_db = [
        {"name": "Aarav Kumar", "roll": "2023CS101", "email": "aarav.kumar@email.com", "course": "CSE", "reg_date": "10 May 2025", "status": "Verified", "reports": 3},
        {"name": "Priya Sharma", "roll": "2023CS102", "email": "priya.sharma@email.com", "course": "CSE", "reg_date": "09 May 2025", "status": "Verified", "reports": 1},
        {"name": "Rohan Das", "roll": "2023CS103", "email": "rohan.das@email.com", "course": "ECE", "reg_date": "08 May 2025", "status": "Verified", "reports": 2},
        {"name": "Sneha Patra", "roll": "2023CS104", "email": "sneha.patra@email.com", "course": "IT", "reg_date": "08 May 2025", "status": "Verified", "reports": 1},
        {"name": "Aditya Verma", "roll": "2023CS105", "email": "aditya.verma@email.com", "course": "CSE", "reg_date": "07 May 2025", "status": "Verified", "reports": 1}
    ]

# ---------------------------------------------------------
# Helper Component: Brand & Logo Panel
# ---------------------------------------------------------
def render_brand_left_panel():
    logo_path = "frontend/assets/logo.png"
    logo_col, name_col = st.columns([1, 4], gap="small")
    with logo_col:
        if os.path.exists(logo_path):
            st.image(logo_path, width=48)
    with name_col:
        st.markdown(
            '<div style="height:48px; display:flex; align-items:center; font-size:1.5rem; font-weight:800; '
            'color:#0f172a; letter-spacing:-0.01em;">Proctor'
            '<span style="background:linear-gradient(90deg,#2563eb,#7c3aed); -webkit-background-clip:text; '
            '-webkit-text-fill-color:transparent;">IQ</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<p style="color: #64748b; font-weight: 600; font-size: 0.95rem; margin-top: 6px;">Upload • Analyze • Score</p>', unsafe_allow_html=True)
    st.markdown('<div class="main-title">AI-Powered Proctoring.</div>', unsafe_allow_html=True)
    st.markdown('<div class="gradient-subtitle">Smarter & Fairer Evaluations.</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #475569; font-size: 0.95rem; line-height: 1.6; margin-bottom: 24px;">Upload proctoring images and let AI detect suspicious activities, calculate a risk score, and generate a detailed risk report automatically.</p>', unsafe_allow_html=True)
    
    features = [
        ("🛡️ Accurate Analysis", "AI models detect suspicious activities from uploaded examination images."),
        ("📊 Risk Scoring", "Calculate a detailed risk score from detected evidence and suspicious activities."),
        ("🔒 Secure & Private", "Student information, identity data, examination images and reports are securely stored.")
    ]
    for title, desc in features:
        st.markdown(f"""
        <div class="feature-card">
            <b style="color: #1e293b; font-size: 0.95rem;">{title}</b>
            <p style="color: #64748b; font-size: 0.85rem; margin: 4px 0 0 0;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# View 1: Main Landing / Login Page
# ---------------------------------------------------------
def show_login_page():
    left_col, _, right_col = st.columns([1.1, 0.1, 1.2])
    
    with left_col:
        render_brand_left_panel()
        
    with right_col:
        st.markdown('<div class="portal-card">', unsafe_allow_html=True)
        st.markdown('<h2 style="font-weight: 800; color: #0f172a; margin-bottom: 4px;">ProctorIQ Portal</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color: #64748b; font-size: 0.9rem; margin-bottom: 20px;">Choose your account type to continue.</p>', unsafe_allow_html=True)
        
        tab_admin, tab_student = st.tabs(["🛡️ Admin Login", "🎓 Student Login"])
        
        with tab_admin:
            st.markdown('<p style="font-size: 0.85rem; color: #64748b; margin-top: 10px;">Access student registration, image analysis and risk reports.</p>', unsafe_allow_html=True)
            admin_email = st.text_input("Admin Email", placeholder="admin@proctor.ai", key="adm_em")
            admin_pass = st.text_input("Password", type="password", placeholder="Enter your password", key="adm_pw")
            
            remember = st.checkbox("Remember me", key="adm_rem")
            if st.button("➜ Enter Admin Portal", use_container_width=True, key="btn_adm_login"):
                if admin_email and admin_pass:
                    st.session_state.auth_status = True
                    st.session_state.user_role = "Admin"
                    st.session_state.current_user = "Administrator"
                    st.rerun()
                else:
                    st.error("Please fill in all fields")
                    
        with tab_student:
            st.markdown('<p style="font-size: 0.85rem; color: #64748b; margin-top: 10px;">View your profile, exam records and verified risk reports.</p>', unsafe_allow_html=True)
            stu_id = st.text_input("Student Email / Roll Number", placeholder="student@example.com or STU2026001", key="stu_id_inp")
            stu_pass = st.text_input("Student Password", type="password", placeholder="••••••••", key="stu_pw")
            
            if st.button("➜ Enter Student Portal", use_container_width=True, key="btn_stu_login"):
                if stu_id and stu_pass:
                    st.session_state.auth_status = True
                    st.session_state.user_role = "Student"
                    st.session_state.current_user = "Aarav Kumar"
                    st.rerun()
                else:
                    st.error("Please fill in your credentials")
                    
        st.markdown('<hr style="margin: 20px 0; border: none; border-top: 1px solid #e2e8f0;">', unsafe_allow_html=True)
        col_msg, col_btn = st.columns([1.5, 1])
        with col_msg:
            st.markdown('<p style="font-size: 0.9rem; color: #64748b; margin-top: 5px;">New user?</p>', unsafe_allow_html=True)
        with col_btn:
            if st.button("Create Account", use_container_width=True):
                st.session_state.page = 'register'
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# View 2: Registration Page
# ---------------------------------------------------------
def show_registration_page():
    left_col, _, right_col = st.columns([1, 0.1, 1.3])
    
    with left_col:
        render_brand_left_panel()
        
    with right_col:
        st.markdown('<div class="portal-card">', unsafe_allow_html=True)
        st.markdown('<h2 style="font-weight: 800; color: #0f172a; margin-bottom: 4px;">Create Account</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color: #64748b; font-size: 0.9rem; margin-bottom: 20px;">Register for secure access to the Proctoring Risk Scoring System.</p>', unsafe_allow_html=True)
        
        reg_type = st.radio("Select Registration Type", ["🎓 Student Registration", "🛡️ Admin Registration"], horizontal=True)
        
        if reg_type == "🎓 Student Registration":
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name", placeholder="Enter full name")
                email = st.text_input("Email Address", placeholder="student@example.com")
                pw = st.text_input("Password", type="password", placeholder="Student@123", help="Must contain 8+ chars, 1 uppercase, 1 digit, 1 special character")
            with c2:
                roll = st.text_input("Roll Number / Student ID", placeholder="STU2026001")
                dept = st.selectbox("Course / Department", ["Computer Science and Engineering", "Information Technology", "Electronics & Comm.", "Electrical Eng."])
                pw_conf = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
                
            st.markdown("#### Student Identity Verification Data")
            u1, u2 = st.columns(2)
            with u1:
                id_card = st.file_uploader("1. Student ID Card Photo", type=['jpg', 'jpeg', 'png'], help="Used for OCR extraction")
            with u2:
                passport = st.file_uploader("2. Passport Size Photo", type=['jpg', 'jpeg', 'png'], help="Used for Face Matching baseline")
                
            if st.button("➜ Create Student Account", use_container_width=True):
                if name and roll and pw and pw == pw_conf and id_card and passport:
                    with st.spinner("Executing OCR and Reference Face Matching..."):
                        time.sleep(1.5)
                        st.success("✓ Identity Verified! Student account created successfully.")
                        time.sleep(1)
                        st.session_state.page = 'login'
                        st.rerun()
                else:
                    st.warning("Please complete all profile details and identity image uploads.")
                    
        else:
            admin_name = st.text_input("Admin Name", placeholder="Enter admin name")
            admin_email = st.text_input("Admin Email", placeholder="admin@example.com")
            apw1 = st.text_input("Password", type="password", placeholder="Create password")
            apw2 = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
            
            if st.button("➜ Create Admin Account", use_container_width=True):
                if admin_name and admin_email and apw1 and apw1 == apw2:
                    st.success("Admin Account created successfully!")
                    time.sleep(1)
                    st.session_state.page = 'login'
                    st.rerun()
                else:
                    st.warning("Please verify your input fields.")

        if st.button("Back to Login", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Component (Role-Aware)
# ---------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        logo_path = "frontend/assets/logo.png"
        logo_col, name_col = st.columns([1, 3], gap="small")
        with logo_col:
            if os.path.exists(logo_path):
                st.image(logo_path, width=36)
        with name_col:
            st.markdown(
                '<div style="height:36px; display:flex; align-items:center; font-size:1.1rem; font-weight:800; '
                'color:#ffffff; letter-spacing:-0.01em;">Proctor'
                '<span style="background:linear-gradient(90deg,#60a5fa,#c084fc); -webkit-background-clip:text; '
                '-webkit-text-fill-color:transparent;">IQ</span></div>',
                unsafe_allow_html=True,
            )

        st.markdown(f"<p style='color:#94a3b8; font-size:0.85rem;'>Logged as: <b style='color:white;'>{st.session_state.user_role}</b></p>", unsafe_allow_html=True)
        st.markdown("---")
        
        if st.session_state.user_role == "Admin":
            nav_options = ["Dashboard", "Students", "Upload & Analyze", "Reports"]
        else:
            nav_options = ["Dashboard", "My Profile", "My Reports"]
            
        selected = st.radio("Navigation", nav_options, index=nav_options.index(st.session_state.active_nav) if st.session_state.active_nav in nav_options else 0)
        st.session_state.active_nav = selected
        
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            st.session_state.auth_status = False
            st.session_state.user_role = None
            st.session_state.page = 'login'
            st.rerun()

# ---------------------------------------------------------
# View 3: Admin Flow Views
# ---------------------------------------------------------
def show_admin_dashboard():
    st.markdown('<div class="main-title">Welcome, Administrator 👋</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #64748b; margin-bottom: 24px;">Manage registered students, analyze examination images and review AI-generated risk reports.</p>', unsafe_allow_html=True)
    
    # 4 Statistic Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="stat-box"><span class="stat-label">Total Students</span><div class="stat-number">125</div><span style="color:#10b981; font-size:0.8rem;">+12 this week</span></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="stat-box"><span class="stat-label">Analyzed Exams</span><div class="stat-number">58</div><span style="color:#3b82f6; font-size:0.8rem;">+5 this week</span></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="stat-box"><span class="stat-label">Reports Generated</span><div class="stat-number">42</div><span style="color:#8b5cf6; font-size:0.8rem;">+7 this week</span></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="stat-box"><span class="stat-label">High Risk Cases</span><div class="stat-number" style="color:#ef4444;">08</div><span style="color:#ef4444; font-size:0.8rem;">⚠️ Needs review</span></div>', unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1.6, 1])
    with col_left:
        st.markdown('<div class="portal-card">', unsafe_allow_html=True)
        st.markdown("#### Recent Analyses")
        recent_data = {
            "Student": ["Aarav Kumar", "Priya Sharma", "Rohan Das", "Sneha Patra", "Aditya Verma"],
            "Roll Number": ["2023CS101", "2023CS102", "2023CS103", "2023CS104", "2023CS105"],
            "Risk Score": ["82%", "45%", "91%", "22%", "67%"],
            "Risk Level": ["High", "Medium", "Critical", "Low", "Medium"]
        }
        st.dataframe(pd.DataFrame(recent_data), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_right:
        st.markdown('<div class="portal-card">', unsafe_allow_html=True)
        st.markdown("#### Quick Actions")
        if st.button("📤 Upload New Proctoring Image", use_container_width=True):
            st.session_state.active_nav = "Upload & Analyze"
            st.rerun()
        if st.button("📑 View All Reports", use_container_width=True):
            st.session_state.active_nav = "Reports"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def show_admin_students():
    st.markdown('<div class="main-title">Students Database</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #64748b;">View and verify all registered students in the system.</p>', unsafe_allow_html=True)
    
    search_q = st.text_input("🔍 Search by Roll Number / Student Name", placeholder="e.g. 2023CS101 or Aarav")
    
    df = pd.DataFrame(st.session_state.students_db)
    if search_q:
        df = df[df['name'].str.contains(search_q, case=False) | df['roll'].str.contains(search_q, case=False)]
        
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("#### Selected Student Profile Inspection")
    selected_roll = st.selectbox("Select Roll Number for deep inspection", df['roll'].tolist())
    student_info = next(item for item in st.session_state.students_db if item["roll"] == selected_roll)
    
    p1, p2, p3 = st.columns([1, 1.5, 1.5])
    with p1:
        st.markdown('<div class="portal-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown("👤")
        st.markdown(f"**{student_info['name']}**<br><span style='color:#64748b;'>{student_info['roll']}</span>", unsafe_allow_html=True)
        st.markdown('<div class="risk-low" style="margin-top:10px;">✓ Identity Verified</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with p2:
        st.markdown('<div class="portal-card">', unsafe_allow_html=True)
        st.write(f"**Email:** {student_info['email']}")
        st.write(f"**Department:** {student_info['course']}")
        st.write(f"**Registered:** {student_info['reg_date']}")
        st.markdown('</div>', unsafe_allow_html=True)
    with p3:
        st.markdown('<div class="portal-card">', unsafe_allow_html=True)
        if st.button("Analyze Proctoring Image for Student", use_container_width=True):
            st.session_state.active_nav = "Upload & Analyze"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def show_admin_upload_analyze():
    st.markdown('<div class="main-title">Upload & Analyze Exam Image</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #64748b;">Select student, upload captured session image, and run the Risk Scoring Agent pipeline.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.markdown('<div class="portal-card">', unsafe_allow_html=True)
        st.markdown("#### Step 1: Select Student")
        student_roll = st.selectbox("Roll Number / Student ID", [s['roll'] for s in st.session_state.students_db])
        st.markdown("#### Step 2: Upload Image")
        uploaded_file = st.file_uploader("Upload Exam / Proctoring Image", type=['jpg', 'jpeg', 'png'])
        if uploaded_file:
            st.image(uploaded_file, caption="Candidate Frame Preview", use_container_width=True)
        
        analyze_btn = st.button("🔍 Analyze Image", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="portal-card">', unsafe_allow_html=True)
        st.markdown("#### Analysis Result & Risk Assessment")
        
        if analyze_btn:
            with st.spinner("Executing Detection Pipeline (YOLO + Pose + Risk Rules)..."):
                time.sleep(2)
                
            m1, m2 = st.columns(2)
            with m1:
                st.markdown('<div class="stat-box"><span class="stat-label">Calculated Score</span><div class="stat-number" style="color:#ef4444;">82 / 100</div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown('<div class="stat-box"><span class="stat-label">Assigned Level</span><div class="stat-number risk-high" style="font-size:1.4rem; margin-top:5px;">HIGH RISK</div></div>', unsafe_allow_html=True)
                
            st.markdown("##### Detected Malpractice Evidence")
            evidences = [
                ("👤 Additional Person in Background", "Confidence: 82%", "risk-high"),
                ("📱 Mobile Phone Detected in Hand", "Confidence: 89%", "risk-high"),
                ("🎧 Earbud / Bluetooth Device Detected", "Confidence: 67%", "risk-medium"),
                ("👁️ Looking Away from Screen Multiple Times", "Confidence: 76%", "risk-medium")
            ]
            for ev, conf, badge in evidences:
                st.markdown(f"- {ev} `({conf})`")
                
            st.markdown("##### AI Explanation")
            st.info("The uploaded exam frame indicates multiple high-severity integrity violations. Another person is visible in background, a mobile phone is detected in hand, and frequent off-screen gaze directions were registered.")
            
            if st.button("📤 Publish Risk Report to Student Notice Board", use_container_width=True):
                st.success("Report Published Successfully ✓. Student can now download the notice.")
        else:
            st.write("Upload an image and click **Analyze Image** to view detections, risk score, and the LLM agent explanation.")
            
        st.markdown('</div>', unsafe_allow_html=True)

def show_admin_reports():
    st.markdown('<div class="main-title">Reports Management</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #64748b;">View and manage generated proctoring reports across all candidates.</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="portal-card">', unsafe_allow_html=True)
    reports = pd.DataFrame([
        {"Report ID": "RPT-2025-00642", "Student": "Aarav Kumar", "Roll": "2023CS101", "Risk Score": "82/100", "Risk Level": "High", "Date": "16 August 2026", "Status": "Published"},
        {"Report ID": "RPT-2025-00643", "Student": "Priya Sharma", "Roll": "2023CS102", "Risk Score": "45/100", "Risk Level": "Medium", "Date": "16 August 2026", "Status": "Published"},
        {"Report ID": "RPT-2025-00644", "Student": "Rohan Das", "Roll": "2023CS103", "Risk Score": "91/100", "Risk Level": "Critical", "Date": "15 August 2026", "Status": "Published"},
        {"Report ID": "RPT-2025-00645", "Student": "Sneha Patra", "Roll": "2023CS104", "Risk Score": "22/100", "Risk Level": "Low", "Date": "15 August 2026", "Status": "Published"},
    ])
    st.dataframe(reports, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# View 4: Student Flow Views
# ---------------------------------------------------------
def show_student_dashboard():
    st.markdown(f'<div class="main-title">Welcome, {st.session_state.current_user} 👋</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #64748b;">Here is your proctoring dashboard and risk notifications.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.4])
    with col1:
        st.markdown('<div class="portal-card">', unsafe_allow_html=True)
        st.markdown("#### Profile Summary")
        st.write(f"**Name:** {st.session_state.current_user}")
        st.write("**Roll Number:** 2023CS101")
        st.write("**Course:** Computer Science and Engineering")
        st.write("**Registration Status:** `Verified ✓`")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="portal-card">', unsafe_allow_html=True)
        st.markdown("#### 📢 Notice Board")
        st.warning("""
        **New Risk Report Available**  
        Your recent examination integrity report has been generated.  
        • **Risk Score:** 82 / 100  
        • **Risk Level:** HIGH  
        • **Date:** 16 August 2026
        """)
        st.button("📥 Download Your Risk Report (PDF)", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def show_student_profile():
    st.markdown('<div class="main-title">My Profile</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #64748b;">Verified enrollment and identity registration details.</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="portal-card">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Personal & Academic Details")
        st.write(f"**Full Name:** {st.session_state.current_user}")
        st.write("**Roll Number:** 2023CS101")
        st.write("**Department:** Computer Science and Engineering")
        st.write("**Institutional Email:** aarav.kumar@email.com")
        st.write("**Registration Date:** 10 May 2025")
    with c2:
        st.markdown("#### Identity Information")
        st.markdown('<div class="risk-low">✓ ID & Biometric Verification Passed</div>', unsafe_allow_html=True)
        st.write("**Student ID OCR Match:** 100%")
        st.write("**Face Biometric Match:** 98.4%")
    st.markdown('</div>', unsafe_allow_html=True)

def show_student_reports():
    st.markdown('<div class="main-title">My Exam Risk Reports</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #64748b;">Review AI-generated inspection summaries for your assessments.</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="portal-card">', unsafe_allow_html=True)
    st.markdown("### Risk Report #001")
    st.write("**Date:** 16 August 2026")
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Risk Score", "82 / 100")
    with c2:
        st.markdown("<p style='color:#64748b; font-size:0.85rem;'>Risk Assessment</p><div class='risk-high'>HIGH RISK</div>", unsafe_allow_html=True)
        
    st.markdown("#### AI Explanation")
    st.write("Multiple suspicious activities were detected during the examination session, including mobile phone presence in hand and secondary individual in background frame.")
    
    st.button("📥 Download Official Report", key="dl_rep_1")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Application Router
# ---------------------------------------------------------
if not st.session_state.auth_status:
    if st.session_state.page == 'login':
        show_login_page()
    else:
        show_registration_page()
else:
    render_sidebar()
    if st.session_state.user_role == "Admin":
        if st.session_state.active_nav == "Dashboard":
            show_admin_dashboard()
        elif st.session_state.active_nav == "Students":
            show_admin_students()
        elif st.session_state.active_nav == "Upload & Analyze":
            show_admin_upload_analyze()
        elif st.session_state.active_nav == "Reports":
            show_admin_reports()
    else:
        if st.session_state.active_nav == "Dashboard":
            show_student_dashboard()
        elif st.session_state.active_nav == "My Profile":
            show_student_profile()
        elif st.session_state.active_nav == "My Reports":
            show_student_reports()