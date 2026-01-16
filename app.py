import streamlit as st
import pandas as pd
try:
    from streamlit_gsheets import GSheetsConnection
except ImportError:
    st.error("Please run: pip install st-gsheets-connection")
from datetime import datetime
from io import BytesIO
import gc

# --- 1. IMMUTABLE UI CONFIGURATION ---
st.set_page_config(page_title="BROBOND", layout="wide", initial_sidebar_state="expanded")
gc.collect()

# --- 2. PERMANENT STYLING (SINGLE LINE MENU LOCK) ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important; }
    
    /* Increased Sidebar Width to fit text in one line */
    [data-testid="stSidebar"] { 
        background-color: #ffffff !important; 
        min-width: 420px !important; 
        max-width: 420px !important; 
        border-right: 2px solid #e6e9ef !important; 
    }
    
    .brand-title { font-size: 62px !important; font-weight: 900 !important; text-align: center; color: #1E1E1E !important; margin-top: 5px !important; }
    .brand-sub { font-size: 16px !important; text-align: center; font-weight: 700 !important; color: #666 !important; margin-bottom: 30px !important; text-transform: uppercase; }
    
    .cat-label { 
        background-color: #f1f3f6 !important; 
        padding: 20px !important; 
        font-weight: 800 !important; 
        font-size: 24px !important; 
        text-align: center !important; 
        margin-bottom: 30px !important; 
        border-radius: 8px !important; 
        color: #1E1E1E !important; 
        text-transform: uppercase !important;
        border: 2px solid #d1d5db !important;
    }

    /* NAVIGATION OPTIONS (LOCKED TO SINGLE LINE) */
    div[data-testid="stRadio"] label p { 
        font-size: 26px !important; 
        font-weight: 700 !important; 
        color: #2C3E50 !important; 
        white-space: nowrap !important; /* Forces text into one line */
        margin-bottom: 12px !important;
    }

    .stButton>button { width: 100% !important; border-radius: 6px !important; height: 4em !important; background-color: #1E1E1E !important; color: white !important; font-weight: 800 !important; font-size: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE CONNECTION ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    pass

# --- 4. NAVIGATION SYSTEM ---
is_form_only = st.query_params.get("view") == "form"

if not is_form_only:
    with st.sidebar:
        st.markdown('<div class="brand-title">BROBOND</div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-sub">A BRAND BY SNBPL</div>', unsafe_allow_html=True)
        st.markdown('<div class="cat-label">Management System</div>', unsafe_allow_html=True)
        menu = st.radio("Navigation", [
            "📊 SALES DASHBOARD", 
            "📞 MASTER LEADS", 
            "🤝 CHANNEL PARTNERS", 
            "💸 EXPENSE TRACKER", 
            "👤 HRM (AYUSH)", 
            "👑 CEO DESK", 
            "💼 MD PANEL"
        ], label_visibility="collapsed")
else:
    menu = "🤝 CHANNEL PARTNERS"

# --- 5. MASTER LEADS SECTION ---
if menu == "📞 MASTER LEADS":
    st.markdown("# 🛡️ MASTER LEAD REPOSITORY")
    lead_cols = ["Lead", "Owner", "First Name", "Last Name", "Email", "Mobile Cc", "Mobile", "REMARK", "Designation", "Phone Co", "Phone", "Lead Source", "Sub Lead Source", "Lead Status", "Industry", "Department", "Annual Revenue", "Company", "Country", "State", "City", "Street", "Pincode", "Lead Priority", "Description", "Product", "Date"]
    if 'lead_data' not in st.session_state:
        st.session_state.lead_data = pd.DataFrame(columns=lead_cols)
    with st.expander("📥 BULK DATA IMPORT", expanded=True):
        uploaded_lead = st.file_uploader("Upload Excel Spreadsheet", type=["xlsx"])
        if st.button("EXECUTE IMPORT"):
            if uploaded_lead:
                st.session_state.lead_data = pd.read_excel(uploaded_lead)
                st.success("Data synchronization successful.")
    if not st.session_state.lead_data.empty:
        towrite = BytesIO()
        st.session_state.lead_data.to_excel(towrite, index=False)
        st.download_button(label="📤 DOWNLOAD LEADS EXCEL", data=towrite.getvalue(), file_name="BROBOND_Leads.xlsx")
        st.dataframe(st.session_state.lead_data, use_container_width=True, height=550)

# --- 6. CHANNEL PARTNERS SECTION ---
elif menu == "🤝 CHANNEL PARTNERS":
    st.markdown("# 🤝 CHANNEL PARTNER MANAGEMENT")
    category = st.selectbox("SELECT PARTNER TYPE", ["Primary Stockist (SS)", "Retail Distributor (DB)", "Logistics Agent (CFA)"])
    with st.form("partner_form", clear_on_submit=True):
        st.subheader(f"Strategic Partnership Form: {category}")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Entity / Registered Firm Name")
            contact = st.text_input("Primary Contact Number")
            state = st.text_input("Operating State")
        with c2:
            city = st.text_input("Operating City")
            address = st.text_input("Registered Office Address")
        if category == "Primary Stockist (SS)":
            f1 = st.text_input("Warehousing Capacity (Sq Ft)")
            f2 = st.text_input("Financial Investment Capacity")
        elif category == "Retail Distributor (DB)":
            f1 = st.text_input("Active Retail Network Size")
            f2 = st.text_input("Existing Brand Portfolio")
        else:
            f1 = st.text_input("GSTIN Details")
            f2 = st.text_input("Fleet Management Details")
        remarks = st.text_area("Executive Summary / Discussion Notes")
        if st.form_submit_button("SUBMIT PARTNER DATA"):
            new_data = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Category": category, "Name": name, "Contact": contact,
                "State": state, "City": city, "Address": address,
                "Detail_1": f1, "Detail_2": f2, "Remarks": remarks
            }])
            try:
                existing = conn.read(worksheet="Sheet1")
                updated = pd.concat([existing, new_data], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated)
                st.success("Cloud Database Updated.")
            except:
                conn.update(worksheet="Sheet1", data=new_data)
                st.success("Database Initialized.")
    if not is_form_only:
        st.divider()
        st.subheader("📊 Live Channel Partner Database")
        try:
            df_p = conn.read(worksheet="Sheet1")
            if not df_p.empty:
                towrite_p = BytesIO()
                df_p.to_excel(towrite_p, index=False)
                st.download_button(label="📤 DOWNLOAD PARTNERS EXCEL", data=towrite_p.getvalue(), file_name="BROBOND_Partners.xlsx")
                st.dataframe(df_p, use_container_width=True)
        except:
            st.info("Syncing with cloud...")
else:
    st.title(menu)
    st.info("Module Locked.")
