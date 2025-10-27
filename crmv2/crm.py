# CRM System - Professional Enterprise Edition with Insurance Module
# Burgundy Maroon & White Theme - Minimal & Professional
# FULLY OPTIMIZED WITH REAL-TIME UPDATES

import streamlit as st
import streamlit.components.v1 as components
import json
import os
from datetime import datetime, timedelta, date
import bcrypt
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from typing import Dict, List, Any
import time
from PIL import Image
import base64

# ====================
# CONFIGURATION
# ====================
st.set_page_config(
    page_title="CRM System - Enterprise",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# File paths
DATA_FILE = "crm_data.json"
UPLOAD_DIR = "uploads"
AADHAR_DIR = os.path.join(UPLOAD_DIR, "aadhar_cards")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AADHAR_DIR, exist_ok=True)

# Theme colors
PRIMARY_COLOR = "#800020"
SECONDARY_COLOR = "#a0153e"
ACCENT_COLOR = "#991b1b"
BACKGROUND_COLOR = "#ffffff"
CARD_BG = "#fafafa"
TEXT_PRIMARY = "#1f2937"
TEXT_SECONDARY = "#6b7280"
BORDER_COLOR = "#e5e7eb"
SHADOW = "0 1px 3px 0 rgba(0, 0, 0, 0.1)"

# Status colors for insurance
INSURANCE_STATUS_COLORS = {
    "submitted": "#dc2626",
    "approved_by_branch_manager": "#ea580c",
    "approved_by_area_manager": "#d97706",
    "approved_by_agm": "#16a34a",
    "rejected": "#991b1b"
}

# Status labels
STATUS_LABELS = {
    "submitted": ("Submitted", "#dc2626"),
    "approved_by_branch_manager": ("Branch Manager Approved", "#ea580c"),
    "approved_by_area_manager": ("Area Manager Approved", "#d97706"),
    "approved_by_agm": ("AGM Approved", "#16a34a"),
    "rejected": ("Rejected", "#991b1b")
}


# ====================
# DATA FUNCTIONS - ✅ FIXED: Removed caching for real-time updates
# ====================

def load_data() -> Dict[str, Any]:
    """Load data from JSON file with proper initialization - NO CACHING"""
    default = {
        "users": {},
        "customers": {},
        "leads": [],
        "customer_leads": [],
        "insurance_entries": [],
        "reliant_best_entries": [],
        "dashboard": {
            "text": "Welcome to CRM System. Please login to continue.",
            "image_path": None
        },
        "credits_fin_entries": [],
        "bids": [],
    }

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return default

        # Ensure all keys exist
        data.setdefault("users", {})
        data.setdefault("customers", {})

        # Convert leads dict to list if needed
        leads_val = data.get("leads", [])
        data["leads"] = list(leads_val.values()) if isinstance(leads_val, dict) else leads_val or []

        data.setdefault("customer_leads", [])
        data.setdefault("insurance_entries", [])
        data.setdefault("reliant_best_entries", [])
        data.setdefault("credits_fin_entries", [])
        data.setdefault("bids", [])
        data.setdefault("dashboard", default["dashboard"])

        # Ensure submitted_by field exists
        for lead in data["leads"]:
            if "submitted_by" not in lead:
                lead["submitted_by"] = lead.get("staff_name") or "unknown"

        return data

    return default


def save_data(data: Dict[str, Any]) -> bool:
    """Save data to JSON file"""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False


def hash_password(pw: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def check_password(pw: str, hashed: str) -> bool:
    """Check password against hashed version"""
    try:
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    except:
        return False


def generate_customer_id(leads_list: List[Dict[str, Any]]) -> str:
    """Generate unique customer ID"""
    last_id = 0
    for lead in leads_list:
        try:
            cid = int(str(lead.get("customer_id", "")).lstrip("0") or 0)
            if cid > last_id:
                last_id = cid
        except ValueError:
            continue
    return str(last_id + 1).zfill(3)


def generate_lead_id(leads_list: List[Dict[str, Any]]) -> str:
    """Generate unique lead ID for customer leads"""
    last_id = 0
    for lead in leads_list:
        try:
            lid = int(str(lead.get("lead_id", "")).replace("LEAD-", ""))
            if lid > last_id:
                last_id = lid
        except ValueError:
            continue
    return f"LEAD-{str(last_id + 1).zfill(4)}"


def generate_insurance_entry_id(entries: List[Dict[str, Any]]) -> str:
    """Generate unique insurance entry ID"""
    last_id = 0
    for entry in entries:
        try:
            eid = int(str(entry.get("entry_id", "")).replace("INS-", ""))
            if eid > last_id:
                last_id = eid
        except ValueError:
            continue
    return f"INS-{str(last_id + 1).zfill(4)}"


def generate_insurance_customer_id(entries: List[Dict[str, Any]]) -> str:
    """Generate unique insurance customer ID"""
    last_id = 0
    for entry in entries:
        try:
            cid = int(str(entry.get("customer_id", "")).replace("INSC-", ""))
            if cid > last_id:
                last_id = cid
        except ValueError:
            continue
    return f"INSC-{str(last_id + 1).zfill(5)}"
# ===========================
# STEP 1: ADD RELIANT BEST ID GENERATORS
# ===========================
# PASTE THIS CODE AFTER generate_insurance_customer_id() FUNCTION

def generate_reliant_best_customer_id(entries: List[Dict[str, Any]]) -> str:
    """Generate unique RELIANT BEST customer ID - Format: RB-00001"""
    last_id = 0
    for entry in entries:
        try:
            cid = int(str(entry.get("customer_id", "")).replace("RB-", ""))
            if cid > last_id:
                last_id = cid
        except ValueError:
            continue
    return f"RB-{str(last_id + 1).zfill(5)}"

def generate_reliant_best_entry_id(entries: List[Dict[str, Any]]) -> str:
    if not entries:  # Check if the list is empty
        return "RBE-000001"  # Start with a default if no entries exist
    last_id = 0
    for entry in entries:
        try:
            eid = int(str(entry.get("entry_id", "")).replace("RBE-", ""))
            if eid > last_id:
                last_id = eid
        except ValueError:
            continue
    return f"RBE-{str(last_id + 1).zfill(6)}"
def generate_gl_customer_id(entries: List[Dict[str, Any]]) -> str:
    """Generate unique GOLD (GL) customer ID - Format: GL-00001"""
    last_id = 0
    for entry in entries:
        try:
            cid = int(str(entry.get("customer_id_gl", "")).replace("GL-", ""))
            if cid > last_id:
                last_id = cid
        except ValueError:
            continue
    return f"GL-{str(last_id + 1).zfill(5)}"
def generate_pl_customer_id(entries: List[Dict[str, Any]]) -> str:
    """Generate unique PL customer ID - Format: PL-00001"""
    last_id = 0
    for entry in entries:
        try:
            cid = int(str(entry.get("customer_id_pl", "")).replace("PL-", ""))
            if cid > last_id:
                last_id = cid
        except ValueError:
            continue
    return f"PL-{str(last_id + 1).zfill(5)}"

def generate_credits_fin_entry_id(entries: List[Dict[str, Any]]) -> str:
    """Generate unique Credits FIN entry ID - Format: CF-00001"""
    last_id = 0
    for entry in entries:
        try:
            cid = int(str(entry.get("entry_id", "")).replace("CF-", ""))
            if cid > last_id:
                last_id = cid
        except ValueError:
            continue
    return f"CF-{str(last_id + 1).zfill(5)}"

def generate_bid_id(entries: List[Dict[str, Any]]) -> str:
    """Generate unique Bid ID - Format: BID-00001"""
    last_id = 0
    for entry in entries:
        try:
            bid = int(str(entry.get("bid_id", "")).replace("BID-", ""))
            if bid > last_id:
                last_id = bid
        except ValueError:
            continue
    return f"BID-{str(last_id + 1).zfill(5)}"

def export_to_excel(leads: List[Dict], filename: str = "crm_data.xlsx") -> BytesIO:
    """Export leads to Excel"""
    df = pd.DataFrame(leads)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Leads')
    output.seek(0)
    return output


def export_insurance_to_excel(entries: List[Dict], filename: str = "insurance_data.xlsx") -> BytesIO:
    """Export insurance entries to Excel without image data"""
    export_data = []
    for entry in entries:
        export_data.append({
            "Entry ID": entry.get("entry_id"),
            "Customer ID": entry.get("customer_id"),
            "Date": entry.get("timestamp", "").split(" ")[0],
            "Staff ID": entry.get("staff_id"),
            "Staff Name": entry.get("staff_name"),
            "Branch": entry.get("branch"),
            "Applicant Name": entry.get("applicant_name"),
            "Age": entry.get("age"),
            "Address": entry.get("address"),
            "Phone": entry.get("phone_number"),
            "Aadhar": entry.get("aadhar_number"),
            "Insurance Type": entry.get("insurance_type"),
            "Premium": entry.get("premium"),
            "Status": entry.get("status"),
            "BM Approved By": entry.get("approved_by_bm") or "Pending",
            "BM Approval Time": entry.get("bm_approval_time") or "N/A",
            "AM Approved By": entry.get("approved_by_am") or "Pending",
            "AM Approval Time": entry.get("am_approval_time") or "N/A",
            "AGM Approved By": entry.get("approved_by_agm") or "Pending",
            "AGM Approval Time": entry.get("agm_approval_time") or "N/A",
            "Rejection Reason": entry.get("rejection_reason") or "N/A"
        })

    df = pd.DataFrame(export_data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Insurance')
    output.seek(0)
    return output

# ===========================
# STEP 2: ADD RELIANT BEST EXPORT FUNCTION
# ===========================
# PASTE THIS CODE AFTER export_insurance_to_excel() FUNCTION
def export_reliant_best_to_excel(entries: List[Dict]) -> BytesIO:
    """Export RELIANT BEST entries to Excel with GOLD and PL in ONE row"""
    export_data = []
    for entry in entries:
        # Create single row with all GOLD and PL data
        row_data = {
            "Entry ID": entry.get("entry_id"),
            "Customer ID(GL)": entry.get("customer_id_gl", ""),
            "Date": entry.get("timestamp", "").split(" ")[0],
            "Staff ID": entry.get("staff_id"),
            "Staff Name": entry.get("staff_name"),
            "Branch": entry.get("branch"),
            # GOLD Section
            "Section": "GOLD & PL",
            "GL Loan Number": entry.get("gold_loan_number", ""),
            "GL Name": entry.get("gold_name", ""),
            "Gross Weight (grams)": entry.get("gold_gross_weight", ""),
            "Net Weight (grams)": entry.get("gold_net_weight", ""),
            "Gold Amount": entry.get("gold_amount", ""),
            # PL Section
            "Customer ID(PL)": entry.get("customer_id_pl", ""),
            "PL Loan Number": entry.get("pl_loan_number", ""),
            "PL Name": entry.get("pl_name", ""),
            "PL Amount": entry.get("pl_amount", "")
        }
        export_data.append(row_data)
    df = pd.DataFrame(export_data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Reliant Best')
    output.seek(0)
    return output

def get_image_base64(image_path: str) -> str:
    """Convert image to base64 for display"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

def filter_leads_by_role(leads: List[Dict], user: Dict) -> List[Dict]:
    """Filter leads based on user role for dashboard"""
    role = user.get("role")
    username = user.get("username")

    if role == "admin":
        return leads
    elif role == "branch_staff":
        return [l for l in leads if l.get("submitted_by") == username]
    elif role == "branch_manager":
        assigned_branches = user.get("assigned_branches", [])
        return [l for l in leads if l.get("branch") in assigned_branches]
    elif role == "area_manager":
        assigned_branches = user.get("assigned_branches", [])
        return [l for l in leads if l.get("branch") in assigned_branches]
    elif role == "AGM":
        db = load_data()
        ams = [u for u, d in db["users"].items()
               if d.get("created_by") == username and d.get("role") == "area_manager"]
        branches = []
        for am in ams:
            branches.extend(db["users"][am].get("assigned_branches", []))
        return [l for l in leads if l.get("branch") in branches]
    else:
        return []


def filter_insurance_by_role(entries: List[Dict], user: Dict, db: Dict) -> List[Dict]:
    """Filter insurance entries based on user role"""
    role = user.get("role")
    username = user.get("username")

    if role == "admin":
        return entries
    elif role == "branch_staff":
        return [e for e in entries if e.get("staff_id") == username]
    elif role == "branch_manager":
        assigned_branches = user.get("assigned_branches", [])
        return [e for e in entries if e.get("branch") in assigned_branches]
    elif role == "area_manager":
        assigned_branches = user.get("assigned_branches", [])
        return [e for e in entries if e.get("branch") in assigned_branches]
    elif role == "AGM":
        ams = [u for u, d in db["users"].items()
               if d.get("created_by") == username and d.get("role") == "area_manager"]
        branches = []
        for am in ams:
            branches.extend(db["users"][am].get("assigned_branches", []))
        return [e for e in entries if e.get("branch") in branches]
    else:
        return []


# ===========================
# STEP 3: ADD RELIANT BEST FILTER FUNCTION
# ===========================
# PASTE THIS CODE AFTER filter_insurance_by_role() FUNCTION

def filter_reliant_best_by_role(entries: List[Dict], user: Dict, db: Dict) -> List[Dict]:
    """Filter RELIANT BEST entries based on user role - accessible to BM, AM, AGM, Admin"""
    role = user.get("role")
    username = user.get("username")

    if role == "admin":
        # Admin sees all entries
        return entries

    elif role == "branch_manager":
        # Branch Manager sees entries from their assigned branches
        assigned_branches = user.get("assigned_branches", [])
        return [e for e in entries if e.get("branch") in assigned_branches]

    elif role == "area_manager":
        # Area Manager sees entries from their assigned branches
        assigned_branches = user.get("assigned_branches", [])
        return [e for e in entries if e.get("branch") in assigned_branches]

    elif role == "AGM":
        # AGM sees all entries under their assigned area managers' branches
        ams = [u for u, d in db["users"].items()
               if d.get("created_by") == username and d.get("role") == "area_manager"]
        branches = []
        for am in ams:
            branches.extend(db["users"][am].get("assigned_branches", []))
        return [e for e in entries if e.get("branch") in branches]

    else:
        # Branch Staff and others have no access
        return []
# ====================
# INITIALIZE DATABASE
# ====================
db = load_data()
if "ADMIN" not in db["users"]:
    db["users"]["ADMIN"] = {
        "username": "ADMIN",
        "password": hash_password("ADMIN123#"),
        "role": "admin",
        "department": "All",
        "assigned_branches": [],
        "assigned_products": [],
        "created_by": "system",
        "created_at": str(datetime.now())
    }
    save_data(db)

# ====================
# SESSION STATE INITIALIZATION
# ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "reports"
if "manage_customer_page" not in st.session_state:
    st.session_state.manage_customer_page = "main"
if "insurance_page" not in st.session_state:
    st.session_state.insurance_page = "application"
if "lead_open_times" not in st.session_state:
    st.session_state.lead_open_times = {}
if "insurance_open_times" not in st.session_state:
    st.session_state.insurance_open_times = {}
if "delete_confirm" not in st.session_state:
    st.session_state.delete_confirm = {}
if "gps_data" not in st.session_state:
    st.session_state.gps_data = None
if "show_gps" not in st.session_state:
    st.session_state.show_gps = False
if "show_insurance_entries" not in st.session_state:
    st.session_state.show_insurance_entries = False
if "show_saved_leads" not in st.session_state:
    st.session_state.show_saved_leads = False
if "show_followup" not in st.session_state:
    st.session_state.show_followup = False
if "delete_confirm_lead" not in st.session_state:
    st.session_state.delete_confirm_lead = None
if "reliant_best_page" not in st.session_state:
    st.session_state.reliant_best_page = "main"
if "show_reliant_best_entries" not in st.session_state:
    st.session_state.show_reliant_best_entries = False
if "credits_fin_page" not in st.session_state:
    st.session_state.credits_fin_page = "main"
if "manage_credits_fin_page" not in st.session_state:
    st.session_state.manage_credits_fin_page = "main"


## ====================
# CUSTOM CSS STYLING - FIXED
# ====================
def apply_custom_css():
    """Apply custom CSS styling - Only once per session"""
    st.markdown(f'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {{
        box-sizing: border-box;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}

    html, body, [class*="css"] {{ 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        margin: 0;
        padding: 0;
        width: 100%;
        overflow-x: hidden;
    }}

    .stApp {{ 
        background: {BACKGROUND_COLOR};
        min-height: 100vh;
    }}

    .main .block-container {{ 
        padding: 1.5rem 2rem !important;
        max-width: 100% !important;
    }}

    section[data-testid="stSidebar"] {{
        background: white !important;
        border-right: 1px solid {BORDER_COLOR} !important;
        box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05) !important;
    }}

    section[data-testid="stSidebar"] > div {{
        background: white !important;
        padding: 1.5rem 1rem !important;
    }}

    section[data-testid="stSidebar"] h1 {{
        color: {PRIMARY_COLOR} !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        margin-bottom: 2rem !important;
        padding-bottom: 1rem !important;
        border-bottom: 2px solid {PRIMARY_COLOR} !important;
    }}

    section[data-testid="stSidebar"] .stButton > button {{
        width: 100% !important;
        text-align: left !important;
        padding: 0.75rem 1rem !important;
        margin-bottom: 0.5rem !important;
        background: white !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 8px !important;
        color: {TEXT_PRIMARY} !important;
        font-weight: 600 !important;
        font-size: 0.9375rem !important;
        transition: all 0.2s ease !important;
    }}

    section[data-testid="stSidebar"] .stButton > button:hover {{
        background: rgba(128, 0, 32, 0.05) !important;
        border-color: {PRIMARY_COLOR} !important;
        color: {PRIMARY_COLOR} !important;
        transform: translateX(4px) !important;
    }}

    label {{
        font-size: 1.0625rem !important;
        font-weight: 700 !important;
        color: {TEXT_PRIMARY} !important;
        margin-bottom: 0.75rem !important;
        line-height: 1.6 !important;
        display: block !important;
        letter-spacing: 0.01em !important;
    }}

    div[data-baseweb="select"] {{
        background: white !important;
        border: 2px solid {BORDER_COLOR} !important;
        border-radius: 10px !important;
        min-height: 60px !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.2s ease !important;
    }}

    div[data-baseweb="select"]:hover {{
        border-color: {PRIMARY_COLOR} !important;
        box-shadow: 0 4px 12px rgba(128, 0, 32, 0.15) !important;
        transform: translateY(-1px) !important;
    }}

    .required-field::after {{
        content: " *";
        color: #dc2626;
        font-weight: 700;
    }}

    .form-section {{
        background: {CARD_BG};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-left: 4px solid {PRIMARY_COLOR};
    }}

    .form-section-title {{
        color: {PRIMARY_COLOR};
        font-size: 1.125rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}

    .stButton > button {{
        background: white !important;
        color: {TEXT_PRIMARY} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 6px !important;
        padding: 0.625rem 1rem !important;
        font-weight: 600 !important;
        font-size: 0.9375rem !important;
        box-shadow: none !important;
        transition: all 0.15s ease !important;
        min-height: 42px !important;
        line-height: 1.4 !important;
    }}

    .stButton > button:hover {{
        background: {CARD_BG} !important;
        border-color: {PRIMARY_COLOR} !important;
        color: {PRIMARY_COLOR} !important;
        transform: translateY(-1px);
    }}

    .stButton > button[kind="primary"] {{
        background: {PRIMARY_COLOR} !important;
        color: white !important;
        border: none !important;
    }}

    .stButton > button[kind="primary"]:hover {{
        background: {SECONDARY_COLOR} !important;
    }}

    .user-info-header {{
        text-align: right;
        padding: 0.75rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid {BORDER_COLOR};
    }}

    .user-info {{
        display: inline-flex;
        align-items: center;
        gap: 0.75rem;
        color: {TEXT_SECONDARY};
        font-size: 0.9375rem;
        font-weight: 500;
    }}

    .user-separator {{
        color: {BORDER_COLOR};
    }}

    .clean-card {{
        background: white;
        border: 1px solid {BORDER_COLOR};
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: {SHADOW};
    }}

    .metric-card {{
        background: white;
        border: 1px solid {BORDER_COLOR};
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: {SHADOW};
        transition: transform 0.2s ease;
    }}

    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }}

    .metric-value {{
        font-size: 2.25rem;
        font-weight: 700;
        color: {PRIMARY_COLOR};
        margin-bottom: 0.375rem;
        line-height: 1.2;
    }}

    .metric-label {{
        font-size: 0.875rem;
        color: {TEXT_SECONDARY};
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        line-height: 1.4;
    }}

    h1 {{ 
        font-size: 1.75rem !important; 
        font-weight: 700 !important; 
        color: {TEXT_PRIMARY} !important; 
        margin-bottom: 1.25rem !important;
        line-height: 1.3 !important;
    }}

    h2 {{ 
        font-size: 1.5rem !important; 
        font-weight: 600 !important; 
        color: {TEXT_PRIMARY} !important; 
        margin-bottom: 1rem !important;
        line-height: 1.3 !important;
    }}

    .burgundy-header {{
        color: {PRIMARY_COLOR} !important;
        border-bottom: 2px solid {PRIMARY_COLOR};
        padding-bottom: 0.625rem;
        margin-bottom: 1.25rem;
    }}

    input, textarea {{
        background: white !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 6px !important;
        padding: 0.625rem 0.875rem !important;
        color: {TEXT_PRIMARY} !important;
        font-size: 0.9375rem !important;
        min-height: 42px !important;
        line-height: 1.4 !important;
    }}

    input:focus, textarea:focus {{
        border-color: {PRIMARY_COLOR} !important;
        box-shadow: 0 0 0 3px rgba(128, 0, 32, 0.1) !important;
        outline: none !important;
    }}

    .stSuccess, .stError, .stWarning, .stInfo {{
        padding: 1rem !important;
        border-radius: 8px !important;
        font-size: 0.9375rem !important;
        line-height: 1.5 !important;
    }}

    .insurance-status-badge {{
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 700;
        display: inline-block;
        text-align: center;
    }}

    .status-submitted {{
        background: #dc2626;
        color: white;
    }}

    .status-approved-bm {{
        background: #ea580c;
        color: white;
    }}

    .status-approved-am {{
        background: #d97706;
        color: white;
    }}

    .status-approved-agm {{
        background: #16a34a;
        color: white;
    }}

    .status-rejected {{
        background: #991b1b;
        color: white;
    }}

    .timer-message {{
        background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
        margin-bottom: 1rem;
        text-align: center;
    }}

    .approval-timeline {{
        background: white;
        border: 1px solid {BORDER_COLOR};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }}

    .timeline-step {{
        display: flex;
        align-items: center;
        padding: 1rem;
        border-left: 3px solid {BORDER_COLOR};
        margin-bottom: 1rem;
        position: relative;
    }}

    .timeline-step.completed {{
        border-left-color: #16a34a;
    }}

    .timeline-step.pending {{
        border-left-color: #d97706;
    }}

    .timeline-step.rejected {{
        border-left-color: #dc2626;
    }}

    .delete-confirm-box {{
        background: #fef2f2;
        border: 2px solid #dc2626;
        border-radius: 8px;
        padding: 1.25rem;
        margin: 1rem 0;
    }}

    .delete-confirm-title {{
        color: #dc2626;
        font-weight: 700;
        font-size: 1.125rem;
        margin-bottom: 0.75rem;
    }}

    .lead-badge-hot {{
        background: #dc2626;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 700;
        display: inline-block;
    }}

    .lead-badge-warm {{
        background: #f59e0b;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 700;
        display: inline-block;
    }}

    .lead-badge-cool {{
        background: #3b82f6;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 700;
        display: inline-block;
    }}

    .status-badge {{
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 700;
        display: inline-block;
    }}

    .reliant-best-gold {{
        background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border-left: 5px solid #b45309;
    }}

    .reliant-best-pl {{
        background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #1e3a8a;
    }}

    .gold-section-title {{
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }}

    .pl-section-title {{
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }}
    </style>
    ''', unsafe_allow_html=True)


# Apply CSS only once at module initialization
apply_custom_css()

# ====================
# GPS COMPONENT
# ====================
def render_gps_component():
    """Render GPS location capture component"""

    gps_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }

            body {
                padding: 1rem;
                background: white;
            }

            .gps-container {
                background: linear-gradient(135deg, #800020 0%, #a0153e 100%);
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 4px 12px rgba(128, 0, 32, 0.3);
            }

            .status-header {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                margin-bottom: 1rem;
            }

            .status-icon {
                font-size: 1.5rem;
            }

            .status-text {
                color: white;
                font-size: 1rem;
                font-weight: 600;
            }

            .location-details {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                padding: 1rem;
                color: white;
            }

            .detail-row {
                display: flex;
                justify-content: space-between;
                margin-bottom: 0.5rem;
                font-size: 0.9rem;
            }

            .detail-label {
                opacity: 0.9;
            }

            .detail-value {
                font-weight: 600;
            }

            .error-message {
                background: #dc2626;
                color: white;
                padding: 1rem;
                border-radius: 8px;
                margin-top: 1rem;
            }

            .retry-button {
                background: white;
                color: #800020;
                border: none;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                margin-top: 1rem;
                width: 100%;
                transition: transform 0.2s ease;
            }

            .retry-button:hover {
                transform: translateY(-2px);
            }

            .spinner {
                border: 3px solid rgba(255, 255, 255, 0.3);
                border-top: 3px solid white;
                border-radius: 50%;
                width: 24px;
                height: 24px;
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .hidden {
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="gps-container">
            <div class="status-header" id="statusHeader">
                <div class="spinner" id="spinner"></div>
                <div class="status-text" id="statusText">Requesting location...</div>
            </div>

            <div class="location-details hidden" id="locationDetails">
                <div class="detail-row">
                    <span class="detail-label">📍 Latitude:</span>
                    <span class="detail-value" id="latitude">--</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">📍 Longitude:</span>
                    <span class="detail-value" id="longitude">--</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">🎯 Accuracy:</span>
                    <span class="detail-value" id="accuracy">--</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">🕐 Timestamp:</span>
                    <span class="detail-value" id="timestamp">--</span>
                </div>
            </div>

            <div class="error-message hidden" id="errorMessage"></div>

            <button class="retry-button hidden" id="retryButton" onclick="getLocation()">
                🔄 Retry Location Access
            </button>
        </div>

        <script>
            const statusHeader = document.getElementById('statusHeader');
            const statusText = document.getElementById('statusText');
            const spinner = document.getElementById('spinner');
            const locationDetails = document.getElementById('locationDetails');
            const errorMessage = document.getElementById('errorMessage');
            const retryButton = document.getElementById('retryButton');

            function updateStatus(icon, text, isError = false) {
                statusText.innerHTML = '<span style="margin-right: 0.5rem;">' + icon + '</span>' + text;
                spinner.classList.add('hidden');

                if (isError) {
                    statusHeader.style.background = 'rgba(220, 38, 38, 0.2)';
                }
            }

            function showSuccess(position) {
                const lat = position.coords.latitude.toFixed(6);
                const lon = position.coords.longitude.toFixed(6);
                const acc = Math.round(position.coords.accuracy);
                const time = new Date().toLocaleTimeString();

                updateStatus('✅', 'Location Acquired Successfully');
                locationDetails.classList.remove('hidden');
                errorMessage.classList.add('hidden');
                retryButton.classList.add('hidden');

                document.getElementById('latitude').textContent = lat;
                document.getElementById('longitude').textContent = lon;
                document.getElementById('accuracy').textContent = '±' + acc + 'm';
                document.getElementById('timestamp').textContent = time;

                sessionStorage.setItem('gps_lat', lat);
                sessionStorage.setItem('gps_lon', lon);
                sessionStorage.setItem('gps_acc', acc);
                sessionStorage.setItem('gps_time', time);
                sessionStorage.setItem('gps_status', 'success');
            }

            function showError(error) {
                let message = '';

                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        message = '❌ Location access denied by user. Please grant permission and retry.';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        message = '❌ Location information unavailable. Check GPS settings.';
                        break;
                    case error.TIMEOUT:
                        message = '❌ Location request timed out. Please retry.';
                        break;
                    default:
                        message = '❌ Unknown error occurred. Please try again.';
                }

                updateStatus('❌', 'Location Failed', true);
                errorMessage.textContent = message;
                errorMessage.classList.remove('hidden');
                locationDetails.classList.add('hidden');
                retryButton.classList.remove('hidden');

                sessionStorage.setItem('gps_status', 'error');
            }

            function getLocation() {
                if (!navigator.geolocation) {
                    showError({ code: -1 });
                    errorMessage.textContent = '❌ Geolocation not supported by this browser';
                    return;
                }

                spinner.classList.remove('hidden');
                statusText.textContent = 'Requesting location permission...';
                errorMessage.classList.add('hidden');
                retryButton.classList.add('hidden');
                locationDetails.classList.add('hidden');
                statusHeader.style.background = 'transparent';

                const options = {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 0
                };

                navigator.geolocation.getCurrentPosition(showSuccess, showError, options);
            }

            getLocation();
        </script>
    </body>
    </html>
    """

    return components.html(gps_html, height=250, scrolling=False)

# ===========================
# STEP 7: CREATE RELIANT BEST ENTRY PAGE FUNCTION
# ===========================
# PASTE THIS ENTIRE FUNCTION BEFORE login_page():

def reliant_best_entry_page(user, db_local):
    """RELIANT BEST entry form with GOLD and PL portions - Branch Manager & Above Only"""
    st.markdown(f'<h2 class="burgundy-header">💰 RELIANT BEST Entry</h2>', unsafe_allow_html=True)
    if st.button("← Back"):
        st.session_state.reliant_best_page = "main"
        st.rerun()
    st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)
    # AUTO-FILLED SECTION
    staff_id = user.get("username")
    staff_name = user.get("username")
    branches = user.get("assigned_branches", [])
    branch = branches[0] if branches else "N/A"

    (""
     "")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("👤 Staff ID", value=staff_id, disabled=True, key="rb_staff_id")
    with col2:
        st.text_input("👤 Staff Name", value=staff_name, disabled=True, key="rb_staff_name")
    # Fix for Staff Name (use user.get("full_name") if available, otherwise keep as is)
    staff_name = user.get("full_name", user.get("username"))  # Update this line if you have a full_name field

    with col3:
        st.text_input("🏢 Branch", value=branch, disabled=True, key="rb_branch")  # Add this if you want to show Branch

    st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)  # Spacer for better layout

    with st.form(key="reliant_best_form"):
        st.markdown("### GOLD Section")
        gl_customer_id = st.number_input("Customer ID (GL) *", min_value=1, step=1)  # New field for GL Customer ID
        gold_loan_number = st.text_input("GL Loan Number *")
        gold_name = st.text_input("GL Name *")
        gold_gross_weight = st.number_input("Gross Weight (grams) *", min_value=0.0)
        gold_net_weight = st.number_input("Net Weight (grams) *", min_value=0.0)
        gold_amount = st.number_input("Gold Amount *", min_value=0.0)

        st.markdown("### PL Section")
        pl_customer_id = st.number_input("Customer ID (PL) *", min_value=1, step=1)  # New field for PL Customer ID
        pl_loan_number = st.text_input("PL Loan Number *")
        pl_name = st.text_input("PL Name *")
        pl_amount = st.number_input("PL Amount *", min_value=0.0)

        submitted = st.form_submit_button("Submit Entry")

        if submitted:
            errors = []
            if gl_customer_id == 0:  # Check if GL Customer ID is provided
                errors.append("GL Customer ID is required.")
            if pl_customer_id == 0:  # Check if PL Customer ID is provided
                errors.append("PL Customer ID is required.")
            if not gold_loan_number or not gold_name or gold_gross_weight <= 0:
                errors.append("All GOLD fields are required.")
            # Add more checks as needed

            if errors:
                for error in errors:
                    st.error(error)
            else:
                new_entry = {
                    "entry_id": generate_reliant_best_entry_id(db_local.get("reliant_best_entries", [])),
                    "customer_id_gl": gl_customer_id,  # Save the user-entered GL Customer ID
                    "customer_id_pl": pl_customer_id,  # Save the user-entered PL Customer ID
                    "staff_id": user.get("username"),
                    "staff_name": user.get("full_name", user.get("username")),
                    "branch": (user.get("assigned_branches", [None]) or ["N/A"])[0] or "N/A",
                    "gold_loan_number": gold_loan_number,
                    "gold_name": gold_name,
                    "gold_gross_weight": gold_gross_weight,
                    "gold_net_weight": gold_net_weight,
                    "gold_amount": gold_amount,
                    "pl_loan_number": pl_loan_number,
                    "pl_name": pl_name,
                    "pl_amount": pl_amount,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                db_local["reliant_best_entries"].append(new_entry)
                save_data(db_local)
                st.success("✅ RELIANT BEST Entry saved successfully!")
                st.balloons()
                st.stop()

# ===========================
# STEP 8: CREATE RELIANT BEST MAIN PAGE FUNCTION
# ===========================
# PASTE THIS FUNCTION AFTER reliant_best_entry_page():

def reliant_best_main(user):
    """Main RELIANT BEST page for navigation"""
    st.markdown(f'<h2 class="burgundy-header">💰 RELIANT BEST Portal</h2>', unsafe_allow_html=True)

    st.markdown(f'''
    <div class="clean-card">
        <h3>Welcome, {user.get("username")}!</h3>
        <p>Select an action below to manage RELIANT BEST entries or view reports:</p>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<div style="margin:2rem 0;"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("➕ Create New Entry", use_container_width=True, type="primary"):
            st.session_state.reliant_best_page = "entry"
            st.rerun()

    with col2:
        if st.button("📊 View & Manage", use_container_width=True, type="primary"):
            st.session_state.reliant_best_page = "management"
            st.rerun()

# ===========================
# STEP 9: CREATE RELIANT BEST MANAGEMENT PAGE FUNCTION
# ===========================
# ===========================
# STEP 9: CREATE RELIANT BEST MANAGEMENT PAGE FUNCTION
# ===========================
# PASTE THIS FUNCTION AFTER reliant_best_main():
def reliant_best_management_page(user, db_local):
    """RELIANT BEST management and view page"""
    st.markdown(f'<h2 class="burgundy-header">💰 RELIANT BEST Management</h2>', unsafe_allow_html=True)

    role = user.get("role")
    username = user.get("username")

    # ACCESS CONTROL
    allowed_roles = ["branch_manager", "area_manager", "AGM", "admin"]
    if role not in allowed_roles:
        st.error("❌ Access Denied: Only Branch Managers, Area Managers, AGM, and Admin can access this page.")
        if st.button("← Go Back"):
            st.session_state.page = "reports"
            st.rerun()
        return

    if st.button("← Back"):
        st.session_state.reliant_best_page = "main"
        st.rerun()

    st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)

    # RELOAD DATA
    db_fresh = load_data()
    all_entries = db_fresh.get("reliant_best_entries", [])
    entries = filter_reliant_best_by_role(all_entries, user, db_fresh)

    if not entries:
        st.info("No RELIANT BEST entries found.")
        return

    # METRICS
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total = len(entries)
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total}</div><div class="metric-label">Total Entries</div></div>', unsafe_allow_html=True)
    with col2:
        total_gold_amount = sum([e.get("gold_amount", 0) for e in entries])
        st.markdown(f'<div class="metric-card"><div class="metric-value">₹{total_gold_amount/100000:.1f}L</div><div class="metric-label">Gold Value</div></div>', unsafe_allow_html=True)
    with col3:
        total_pl_amount = sum([e.get("pl_amount", 0) for e in entries])
        st.markdown(f'<div class="metric-card"><div class="metric-value">₹{total_pl_amount/100000:.1f}L</div><div class="metric-label">PL Value</div></div>', unsafe_allow_html=True)
    with col4:
        combined_total = total_gold_amount + total_pl_amount
        st.markdown(f'<div class="metric-card"><div class="metric-value">₹{combined_total/100000:.1f}L</div><div class="metric-label">Total Value</div></div>', unsafe_allow_html=True)

    st.markdown('<div style="margin:2rem 0;"></div>', unsafe_allow_html=True)

    # FILTERS
    st.markdown("### 🔍 Filters")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        branches = sorted(list(set([e.get("branch") for e in entries])))
        branch_filter = st.selectbox("Branch", ["All"] + branches, key="rb_branch_filter")
    with col2:
        if role in ["area_manager", "AGM", "admin"]:
            staff = sorted(list(set([e.get("staff_id") for e in entries if e.get("staff_id")])))
            staff_filter = st.selectbox("Staff", ["All"] + staff, key="rb_staff_filter")
        else:
            staff_filter = "All"
    with col3:
        from_date = st.date_input("From Date", value=date.today() - timedelta(days=30), key="rb_from_date")
    with col4:
        to_date = st.date_input("To Date", value=date.today(), key="rb_to_date")

    st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

    # Apply filters
    filtered = entries
    if branch_filter != "All":
        filtered = [e for e in filtered if e.get("branch") == branch_filter]
    if staff_filter != "All":
        filtered = [e for e in filtered if e.get("staff_id") == staff_filter]
    filtered = [e for e in filtered if from_date <= datetime.strptime(e.get("timestamp", "2000-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S").date() <= to_date]

    st.markdown(f"**Found {len(filtered)} records**")

    # Download button
    if filtered:
        excel_data = export_reliant_best_to_excel(filtered)
        st.download_button(
            label=f"📥 Download Excel Report ({len(filtered)} records)",
            data=excel_data,
            file_name=f"reliant_best_{role}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )

    st.markdown('<div style="margin:2rem 0;"></div>', unsafe_allow_html=True)

    # Display entries
    st.markdown("### 📋 RELIANT BEST Entries")
    for entry in filtered:
        entry_id = entry.get("entry_id")
        customer_id_gl = entry.get("customer_id_gl") or '-'
        customer_id_pl = entry.get("customer_id_pl") or '-'
        gold_amt = entry.get("gold_amount", 0)
        pl_amt = entry.get("pl_amount", 0)
        total_amt = gold_amt + pl_amt

        with st.expander(f"{entry_id} | GL: {customer_id_gl} | PL: {customer_id_pl} | ₹{total_amt:,.0f}"):
            col1, col2 = st.columns(2)

            # GOLD Section
            with col1:
                st.markdown(f"""
                <div class="reliant-best-gold" style="margin:0; padding:0.5rem; border:1px solid #b8860b; border-radius:6px;">
                    <div class="gold-section-title" style="font-weight:bold; color:#b8860b; margin-bottom:0.5rem;">GOLD Section</div>
                    <div style="font-size:0.95rem; line-height:1.6;">
                        <strong>Customer ID (GL):</strong> {customer_id_gl}<br>
                        <strong>Loan Number:</strong> {entry.get('gold_loan_number', '-')}<br>
                        <strong>Applicant Name:</strong> {entry.get('gold_name', '-')}<br>
                        <strong>Gross Weight:</strong> {entry.get('gold_gross_weight', 0)} grams<br>
                        <strong>Net Weight:</strong> {entry.get('gold_net_weight', 0)} grams<br>
                        <strong>Amount:</strong> ₹{gold_amt:,.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # PL Section
            with col2:
                pl_name = entry.get('pl_name') or '-'
                pl_loan_number = entry.get('pl_loan_number') or '-'
                st.markdown(f"""
                <div class="reliant-best-pl" style="margin:0; padding:0.5rem; border:1px solid #0ea5e9; border-radius:6px;">
                    <div class="pl-section-title" style="font-weight:bold; color:#0c63e4; margin-bottom:0.5rem;">PL (Portion) Section</div>
                    <div style="font-size:0.95rem; line-height:1.6;">
                        <strong>Customer ID (PL):</strong> {customer_id_pl}<br>
                        <strong>Loan Number:</strong> {pl_loan_number}<br>
                        <strong>Applicant Name:</strong> {pl_name}<br>
                        <strong>Amount:</strong> ₹{pl_amt:,.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

            # Staff / Branch / Date Info
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"**Staff ID:** {entry.get('staff_id', '-')}")
            with col2:
                st.markdown(f"**Staff Name:** {entry.get('staff_name', '-')}")
            with col3:
                st.markdown(f"**Branch:** {entry.get('branch', '-')}")
            with col4:
                st.markdown(f"**Date:** {entry.get('timestamp', '').split(' ')[0]}")

            st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

            # Combined Total
            st.markdown(f"""
            <div style="background:#f0f9ff; border:2px solid #0ea5e9; border-radius:8px; padding:1rem;">
                <strong style="color:#0c63e4; font-size:1.1rem;">Combined Total: ₹{total_amt:,.2f}</strong>
            </div>
            """, unsafe_allow_html=True)

            # --------- AGM Delete Option ---------
            if role == "AGM":
                if st.button(f"🗑️ Delete Entry", key=f"delete_{entry_id}", use_container_width=True):
                    try:
                        db_fresh["reliant_best_entries"] = [
                            e for e in db_fresh["reliant_best_entries"] if e.get("entry_id") != entry_id
                        ]
                        save_data(db_fresh)
                        st.success("✅ Entry deleted successfully!")
                        st.rerun()  # <-- Updated
                    except Exception as e:
                        st.error(f"❌ Failed to delete entry: {e}")


def filter_credits_fin_by_role(entries: List[Dict], user: Dict) -> List[Dict]:
    """Filter Credits FIN entries by role"""
    role = user.get("role")
    username = user.get("username")
    if role == "admin":
        return entries
    elif role == "branch_manager":
        assigned_branches = user.get("assigned_branches", [])
        return [e for e in entries if e.get("branch") in assigned_branches]
    elif role == "AGM":
        return entries  # AGM sees all for management
    return []

def filter_bids_by_role(entries: List[Dict], user: Dict) -> List[Dict]:
    """Filter Bids by role"""
    role = user.get("role")
    username = user.get("username")
    if role == "admin":
        return entries
    elif role == "branch_manager":
        return [e for e in entries if e.get("bidder") == username]
    elif role == "AGM":
        return entries  # AGM sees all for approval
    return []


# ====================
# LOGIN PAGE
# ====================
def login_page():
    """Login page with professional design"""
    db_local = load_data()

    st.markdown('<div style="margin-top:2rem;"></div>', unsafe_allow_html=True)

    col1, col_div, col2 = st.columns([1, 0.05, 1.2], gap="large")

    with col1:
        st.markdown(f'''
        <div class="clean-card">
            <h1 class="burgundy-header">🔐 Sign In</h1>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)

        with st.form(key="login_form", clear_on_submit=False):
            username = st.text_input("👤 Username", placeholder="Enter username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter password")

            st.markdown('<div style="margin:1.25rem 0;"></div>', unsafe_allow_html=True)

            login_submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

            if login_submitted:
                db_now = load_data()
                if username in db_now["users"]:
                    user_data = db_now["users"][username]
                    if check_password(password, user_data["password"]):
                        st.session_state.logged_in = True
                        st.session_state.user = user_data
                        st.session_state.lead_open_times = {}
                        st.session_state.insurance_open_times = {}
                        st.session_state.delete_confirm = {}
                        st.session_state.gps_data = None
                        st.success(f"✅ Welcome, {username}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("❌ Invalid password.")
                else:
                    st.error("❌ Username not found.")

    with col_div:
        st.markdown(f'<div style="border-left:2px solid {BORDER_COLOR}; height:400px;"></div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'''
        <div class="clean-card">
            <h2 class="burgundy-header">Welcome to CRM System</h2>
            <p style="color:{TEXT_SECONDARY}; line-height:1.8; font-size:1rem;">
                {db_local.get("dashboard", {}).get("text", "Welcome to CRM System. Please login to continue.")}
            </p>
        </div>
        ''', unsafe_allow_html=True)

        img_path = db_local.get("dashboard", {}).get("image_path")
        if img_path and os.path.exists(img_path):
            st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)
            st.image(img_path, use_container_width=True)


# ====================
# INSURANCE APPLICATION PAGE - FULLY CORRECTED
# ====================
def insurance_application_page(user, db_local):
    """Insurance application form for branch staff"""
    st.markdown(f'<h2 class="burgundy-header">🏥 Insurance Application</h2>', unsafe_allow_html=True)

    if st.button("← Back to Manage Customer"):
        st.session_state.manage_customer_page = "main"
        st.rerun()

    st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)

    # AUTO-FILLED SECTION
    staff_id = user.get("username")
    staff_name = user.get("username")
    branch = user.get("assigned_branches", [""])[0] if user.get("assigned_branches") else "N/A"

    st.markdown("### 📋 Staff Information")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.text_input("👤 Staff ID", value=staff_id, disabled=True, key="ins_staff_id")

    with col2:
        st.text_input("👤 Staff Name", value=staff_name, disabled=True, key="ins_staff_name")

    with col3:
        st.text_input("🏢 Branch", value=branch, disabled=True, key="ins_branch")

    st.markdown('<div style="margin:2rem 0;"></div>', unsafe_allow_html=True)

    # APPLICATION FORM
    st.markdown("### 📝 Applicant Details")

    with st.form(key="insurance_application_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            applicant_name = st.text_input(
                "👤 Applicant Name *",
                placeholder="Enter full name",
                key="applicant_name"
            )

            age = st.number_input(
                "🎂 Age *",
                min_value=18,
                max_value=100,
                value=30,
                key="age"
            )

            phone = st.text_input(
                "📞 Phone Number *",
                placeholder="10 digit number",
                max_chars=10,
                key="phone"
            )

        with col2:
            address = st.text_area(
                "📍 Address *",
                placeholder="Enter complete address",
                height=100,
                key="address"
            )

            aadhar = st.text_input(
                "🆔 Aadhar Number *",
                placeholder="12 digit number",
                max_chars=12,
                key="aadhar"
            )

        st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            insurance_type = st.selectbox(
                "🏥 Insurance Type *",
                ["Health", "Hospitalization", "Vehicle"],
                key="insurance_type"
            )

        with col2:
            premium = st.number_input(
                "💰 Premium (₹) *",
                min_value=0.0,
                step=100.0,
                format="%.2f",
                key="premium"
            )

        st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

        st.markdown("### 📄 Document Upload")
        aadhar_file = st.file_uploader(
            "Upload Aadhar Card *",
            type=["jpg", "jpeg", "png", "pdf"],
            help="Maximum file size: 5MB",
            key="aadhar_upload"
        )

        st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)

        submitted = st.form_submit_button("✅ Submit Application", use_container_width=True, type="primary")

        if submitted:
            errors = []

            if not applicant_name:
                errors.append("Applicant name is required")

            if not phone or not phone.isdigit() or len(phone) != 10:
                errors.append("Phone number must be exactly 10 digits")

            if not aadhar or not aadhar.isdigit() or len(aadhar) != 12:
                errors.append("Aadhar number must be exactly 12 digits")

            if not address:
                errors.append("Address is required")

            if premium <= 0:
                errors.append("Premium must be greater than 0")

            if not aadhar_file:
                errors.append("Aadhar card document is required")

            if aadhar_file and aadhar_file.size > 5 * 1024 * 1024:
                errors.append("File size must be less than 5MB")

            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                file_ext = aadhar_file.name.split(".")[-1]
                timestamp = int(datetime.now().timestamp())
                filename = f"aadhar_{staff_id}_{timestamp}.{file_ext}"
                file_path = os.path.join(AADHAR_DIR, filename)

                with open(file_path, "wb") as f:
                    f.write(aadhar_file.getbuffer())

                insurance_entries = db_local.get("insurance_entries", [])
                entry_id = generate_insurance_entry_id(insurance_entries)
                customer_id = generate_insurance_customer_id(insurance_entries)

                new_entry = {
                    "entry_id": entry_id,
                    "customer_id": customer_id,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "staff_id": staff_id,
                    "staff_name": staff_name,
                    "branch": branch,
                    "applicant_name": applicant_name,
                    "age": age,
                    "address": address,
                    "phone_number": phone,
                    "aadhar_number": aadhar,
                    "insurance_type": insurance_type,
                    "premium": premium,
                    "aadhar_photo_path": file_path,
                    "status": "submitted",
                    "approved_by_bm": None,
                    "approved_by_am": None,
                    "approved_by_agm": None,
                    "bm_approval_time": None,
                    "am_approval_time": None,
                    "agm_approval_time": None,
                    "rejection_reason": None,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                insurance_entries.append(new_entry)
                db_local["insurance_entries"] = insurance_entries

                if save_data(db_local):
                    st.success(f"✅ Application submitted successfully!")
                    st.success(f"📋 Entry ID: {entry_id} | Customer ID: {customer_id}")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()

    # VIEW SAVED ENTRIES
    st.markdown('<div style="margin:3rem 0;"></div>', unsafe_allow_html=True)

    if st.button("📊 View My Applications", use_container_width=True, type="secondary"):
        st.session_state.show_insurance_entries = not st.session_state.show_insurance_entries
        st.rerun()

    if st.session_state.show_insurance_entries:
        st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)
        st.markdown("### 📋 My Insurance Applications")

        # ✅ RELOAD DATA HERE FOR REAL-TIME UPDATES
        db_fresh = load_data()
        insurance_entries = db_fresh.get("insurance_entries", [])
        my_entries = [e for e in insurance_entries if e.get("staff_id") == staff_id]

        if not my_entries:
            st.info("No applications found.")
            return

        # Stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total = len(my_entries)
            st.markdown(
                f'<div class="metric-card"><div class="metric-value">{total}</div><div class="metric-label">Total</div></div>',
                unsafe_allow_html=True)
        with col2:
            pending = len([e for e in my_entries if e.get("status") == "submitted"])
            st.markdown(
                f'<div class="metric-card"><div class="metric-value">{pending}</div><div class="metric-label">Pending</div></div>',
                unsafe_allow_html=True)
        with col3:
            approved = len([e for e in my_entries if e.get("status") == "approved_by_agm"])
            st.markdown(
                f'<div class="metric-card"><div class="metric-value">{approved}</div><div class="metric-label">Approved</div></div>',
                unsafe_allow_html=True)
        with col4:
            rejected = len([e for e in my_entries if e.get("status") == "rejected"])
            st.markdown(
                f'<div class="metric-card"><div class="metric-value">{rejected}</div><div class="metric-label">Rejected</div></div>',
                unsafe_allow_html=True)

        st.markdown('<div style="margin:2rem 0;"></div>', unsafe_allow_html=True)

        # Display entries
        for entry in my_entries:
            status = entry.get("status", "submitted")

            if status == "submitted":
                status_class = "status-submitted"
                status_text = "⏳ Pending Approval"
            elif status == "approved_by_branch_manager":
                status_class = "status-approved-bm"
                status_text = "✅ Branch Manager Approved"
            elif status == "approved_by_area_manager":
                status_class = "status-approved-am"
                status_text = "✅ Area Manager Approved"
            elif status == "approved_by_agm":
                status_class = "status-approved-agm"
                status_text = "✅ Fully Approved (AGM)"
            elif status == "rejected":
                status_class = "status-rejected"
                status_text = "❌ Rejected"
            else:
                status_class = "status-submitted"
                status_text = "⏳ Unknown Status"

            with st.expander(f"{entry.get('entry_id')} | {entry.get('customer_id')} | {entry.get('applicant_name')}"):
                st.markdown(f'<div class="insurance-status-badge {status_class}">{status_text}</div>',
                            unsafe_allow_html=True)

                st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(f"**Applicant:** {entry.get('applicant_name')}")
                    st.markdown(f"**Age:** {entry.get('age')}")
                    st.markdown(f"**Phone:** {entry.get('phone_number')}")

                with col2:
                    st.markdown(f"**Aadhar:** {entry.get('aadhar_number')}")
                    st.markdown(f"**Type:** {entry.get('insurance_type')}")
                    st.markdown(f"**Premium:** ₹{entry.get('premium'):,.2f}")

                with col3:
                    st.markdown(f"**Branch:** {entry.get('branch')}")
                    st.markdown(f"**Date:** {entry.get('timestamp', '').split(' ')[0]}")

                st.markdown("---")
                st.markdown(f"**Address:** {entry.get('address')}")

                if entry.get("aadhar_photo_path") and os.path.exists(entry.get("aadhar_photo_path")):
                    st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)
                    st.markdown("**📄 Aadhar Card:**")

                    file_ext = entry.get("aadhar_photo_path").split(".")[-1].lower()
                    if file_ext in ["jpg", "jpeg", "png"]:
                        st.image(entry.get("aadhar_photo_path"), width=400)
                    else:
                        st.info("PDF document attached. Download to view.")
                        with open(entry.get("aadhar_photo_path"), "rb") as f:
                            st.download_button(
                                label="📥 Download Aadhar",
                                data=f,
                                file_name=f"aadhar_{entry.get('entry_id')}.pdf",
                                mime="application/pdf",
                                key=f"dl_aadhar_app_{entry.get('entry_id')}"
                            )

                if status == "rejected" and entry.get("rejection_reason"):
                    st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)
                    st.error(f"**Rejection Reason:** {entry.get('rejection_reason')}")

                st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)
                st.markdown("**📊 Approval Timeline:**")

                # Build clean timeline
                if entry.get("approved_by_bm"):
                    st.markdown(f"""
                    <div style="padding: 0.75rem; margin-bottom: 0.5rem; border-left: 3px solid #16a34a; background: #f0fdf4; border-radius: 4px;">
                        ✅ <strong>Branch Manager:</strong> {entry.get("approved_by_bm")}<br>
                        <small style="color: #6b7280;">{entry.get("bm_approval_time", "")}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="padding: 0.75rem; margin-bottom: 0.5rem; border-left: 3px solid #d97706; background: #fffbeb; border-radius: 4px;">
                        ⏳ <strong>Branch Manager:</strong> Pending
                    </div>
                    """, unsafe_allow_html=True)

                if entry.get("approved_by_bm"):
                    if entry.get("approved_by_am"):
                        st.markdown(f"""
                        <div style="padding: 0.75rem; margin-bottom: 0.5rem; border-left: 3px solid #16a34a; background: #f0fdf4; border-radius: 4px;">
                            ✅ <strong>Area Manager:</strong> {entry.get("approved_by_am")}<br>
                            <small style="color: #6b7280;">{entry.get("am_approval_time", "")}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="padding: 0.75rem; margin-bottom: 0.5rem; border-left: 3px solid #d97706; background: #fffbeb; border-radius: 4px;">
                            ⏳ <strong>Area Manager:</strong> Pending
                        </div>
                        """, unsafe_allow_html=True)

                if entry.get("approved_by_am"):
                    if entry.get("approved_by_agm"):
                        st.markdown(f"""
                        <div style="padding: 0.75rem; margin-bottom: 0.5rem; border-left: 3px solid #16a34a; background: #f0fdf4; border-radius: 4px;">
                            ✅ <strong>AGM:</strong> {entry.get("approved_by_agm")}<br>
                            <small style="color: #6b7280;">{entry.get("agm_approval_time", "")}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="padding: 0.75rem; margin-bottom: 0.5rem; border-left: 3px solid #d97706; background: #fffbeb; border-radius: 4px;">
                            ⏳ <strong>AGM:</strong> Pending
                        </div>
                        """, unsafe_allow_html=True)

                if status == "submitted":
                    st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

                    col_edit, col_delete = st.columns(2)

                    with col_edit:
                        if st.button("✏️ Edit", key=f"edit_app_{entry.get('entry_id')}", use_container_width=True):
                            st.info("Edit functionality: Re-open form with pre-filled data")

                    with col_delete:
                        delete_key = f"insurance_delete_app_{entry.get('entry_id')}"

                        if st.button("🗑️ Delete", key=f"delete_app_{entry.get('entry_id')}", use_container_width=True):
                            if st.session_state.get(delete_key, False):
                                updated_entries = [e for e in db_local["insurance_entries"] if
                                                   e.get("entry_id") != entry.get("entry_id")]
                                db_local["insurance_entries"] = updated_entries

                                if entry.get("aadhar_photo_path") and os.path.exists(entry.get("aadhar_photo_path")):
                                    try:
                                        os.remove(entry.get("aadhar_photo_path"))
                                    except:
                                        pass

                                if save_data(db_local):
                                    st.success(f"✅ Entry {entry.get('entry_id')} deleted!")
                                    st.session_state[delete_key] = False
                                    time.sleep(1)
                                    st.rerun()
                            else:
                                st.session_state[delete_key] = True
                                st.warning("⚠️ Click delete again to confirm")
                                st.rerun()


# ====================
# INSURANCE MANAGEMENT PAGE
# ====================
def insurance_management_page(user, db_local):
    """Insurance management page for managers"""
    st.markdown(f'<h2 class="burgundy-header">🏥 Insurance Management</h2>', unsafe_allow_html=True)

    role = user.get("role")
    username = user.get("username")

    if role not in ["branch_manager", "area_manager", "AGM", "admin"]:
        st.error("❌ Access Denied")
        return

    if st.button("← Back"):
        st.session_state.page = "reports"
        st.rerun()

    st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)

    # ✅ RELOAD DATA FOR REAL-TIME UPDATES
    db_fresh = load_data()
    all_entries = db_fresh.get("insurance_entries", [])
    entries = filter_insurance_by_role(all_entries, user, db_fresh)

    if not entries:
        st.info("No insurance applications found.")
        return

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total = len(entries)
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{total}</div><div class="metric-label">Total</div></div>',
            unsafe_allow_html=True)
    with col2:
        pending = len([e for e in entries if e.get("status") == "submitted" and role == "branch_manager"])
        if role == "area_manager":
            pending = len([e for e in entries if e.get("status") == "approved_by_branch_manager"])
        elif role == "AGM":
            pending = len([e for e in entries if e.get("status") == "approved_by_area_manager"])
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{pending}</div><div class="metric-label">Pending</div></div>',
            unsafe_allow_html=True)
    with col3:
        approved = len([e for e in entries if e.get("status") == "approved_by_agm"])
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{approved}</div><div class="metric-label">Approved</div></div>',
            unsafe_allow_html=True)
    with col4:
        rejected = len([e for e in entries if e.get("status") == "rejected"])
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{rejected}</div><div class="metric-label">Rejected</div></div>',
            unsafe_allow_html=True)

    st.markdown('<div style="margin:2rem 0;"></div>', unsafe_allow_html=True)

    # Filters
    st.markdown("### 🔍 Filters")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        branches = list(set([e.get("branch") for e in entries]))
        branch_filter = st.selectbox("Branch", ["All"] + branches, key="ins_branch_filter")

    with col2:
        types = ["All", "Health", "Hospitalization", "Vehicle"]
        type_filter = st.selectbox("Insurance Type", types, key="ins_type_filter")

    with col3:
        status_options = ["All", "Pending", "Approved", "Rejected"]
        status_filter = st.selectbox("Status", status_options, key="ins_status_filter")

    with col4:
        st.write("")

    filtered = entries

    if branch_filter != "All":
        filtered = [e for e in filtered if e.get("branch") == branch_filter]

    if type_filter != "All":
        filtered = [e for e in filtered if e.get("insurance_type") == type_filter]

    if status_filter == "Pending":
        if role == "branch_manager":
            filtered = [e for e in filtered if e.get("status") == "submitted"]
        elif role == "area_manager":
            filtered = [e for e in filtered if e.get("status") == "approved_by_branch_manager"]
        elif role == "AGM":
            filtered = [e for e in filtered if e.get("status") == "approved_by_area_manager"]
    elif status_filter == "Approved":
        filtered = [e for e in filtered if e.get("status") == "approved_by_agm"]
    elif status_filter == "Rejected":
        filtered = [e for e in filtered if e.get("status") == "rejected"]

    st.markdown(f"**Found {len(filtered)} applications**")

    if filtered:
        excel_data = export_insurance_to_excel(filtered)
        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name=f"insurance_{role}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.markdown('<div style="margin:2rem 0;"></div>', unsafe_allow_html=True)

    for entry in filtered:
        entry_id = entry.get("entry_id")
        status = entry.get("status", "submitted")

        can_approve = False
        if role == "branch_manager" and status == "submitted":
            can_approve = True
        elif role == "area_manager" and status == "approved_by_branch_manager":
            can_approve = True
        elif role == "AGM" and status == "approved_by_area_manager":
            can_approve = True

        if status == "submitted":
            status_class = "status-submitted"
            status_text = "⏳ Pending BM Approval"
        elif status == "approved_by_branch_manager":
            status_class = "status-approved-bm"
            status_text = "⏳ Pending AM Approval"
        elif status == "approved_by_area_manager":
            status_class = "status-approved-am"
            status_text = "⏳ Pending AGM Approval"
        elif status == "approved_by_agm":
            status_class = "status-approved-agm"
            status_text = "✅ Fully Approved"
        elif status == "rejected":
            status_class = "status-rejected"
            status_text = "❌ Rejected"
        else:
            status_class = "status-submitted"
            status_text = "⏳ Unknown"

        with st.expander(f"{entry_id} | {entry.get('customer_id')} | {entry.get('applicant_name')} | {entry.get('insurance_type')}"):
            st.markdown(f'<div class="insurance-status-badge {status_class}">{status_text}</div>',
                        unsafe_allow_html=True)

            st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"**Staff ID:** {entry.get('staff_id')}")
                st.markdown(f"**Staff Name:** {entry.get('staff_name')}")
                st.markdown(f"**Branch:** {entry.get('branch')}")

            with col2:
                st.markdown(f"**Applicant:** {entry.get('applicant_name')}")
                st.markdown(f"**Age:** {entry.get('age')}")
                st.markdown(f"**Phone:** {entry.get('phone_number')}")

            with col3:
                st.markdown(f"**Aadhar:** {entry.get('aadhar_number')}")
                st.markdown(f"**Type:** {entry.get('insurance_type')}")
                st.markdown(f"**Premium:** ₹{entry.get('premium'):,.2f}")

            st.markdown("---")
            st.markdown(f"**Address:** {entry.get('address')}")

            if entry.get("aadhar_photo_path") and os.path.exists(entry.get("aadhar_photo_path")):
                st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)
                st.markdown("**📄 Aadhar Card Document:**")

                file_ext = entry.get("aadhar_photo_path").split(".")[-1].lower()
                if file_ext in ["jpg", "jpeg", "png"]:
                    st.image(entry.get("aadhar_photo_path"), width=500)
                else:
                    st.info("PDF document attached. Download to view.")
                    with open(entry.get("aadhar_photo_path"), "rb") as f:
                        st.download_button(
                            label="📥 Download Aadhar",
                            data=f,
                            file_name=f"aadhar_{entry_id}.pdf",
                            mime="application/pdf",
                            key=f"download_aadhar_mgmt_{entry_id}"
                        )

            st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)
            st.markdown("**📊 Approval Timeline:**")

            if entry.get("approved_by_bm"):
                st.markdown(f"""
                <div style="padding: 0.75rem; margin-bottom: 0.5rem; border-left: 3px solid #16a34a; background: #f0fdf4; border-radius: 4px;">
                    ✅ <strong>Branch Manager:</strong> {entry.get("approved_by_bm")}<br>
                    <small style="color: #6b7280;">{entry.get("bm_approval_time", "")}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="padding: 0.75rem; margin-bottom: 0.5rem; border-left: 3px solid #d97706; background: #fffbeb; border-radius: 4px;">
                    ⏳ <strong>Branch Manager:</strong> Pending
                </div>
                """, unsafe_allow_html=True)

            if entry.get("approved_by_bm"):
                if entry.get("approved_by_am"):
                    st.markdown(f"""
                    <div style="padding: 0.75rem; margin-bottom: 0.5rem; border-left: 3px solid #16a34a; background: #f0fdf4; border-radius: 4px;">
                        ✅ <strong>Area Manager:</strong> {entry.get("approved_by_am")}<br>
                        <small style="color: #6b7280;">{entry.get("am_approval_time", "")}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="padding: 0.75rem; margin-bottom: 0.5rem; border-left: 3px solid #d97706; background: #fffbeb; border-radius: 4px;">
                        ⏳ <strong>Area Manager:</strong> Pending
                    </div>
                    """, unsafe_allow_html=True)

            if entry.get("approved_by_am"):
                if entry.get("approved_by_agm"):
                    st.markdown(f"""
                    <div style="padding: 0.75rem; margin-bottom: 0.5rem; border-left: 3px solid #16a34a; background: #f0fdf4; border-radius: 4px;">
                        ✅ <strong>AGM:</strong> {entry.get("approved_by_agm")}<br>
                        <small style="color: #6b7280;">{entry.get("agm_approval_time", "")}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="padding: 0.75rem; margin-bottom: 0.5rem; border-left: 3px solid #d97706; background: #fffbeb; border-radius: 4px;">
                        ⏳ <strong>AGM:</strong> Pending
                    </div>
                    """, unsafe_allow_html=True)

            if status == "rejected" and entry.get("rejection_reason"):
                st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)
                st.error(f"**Rejection Reason:** {entry.get('rejection_reason')}")

            if can_approve:
                st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)

                if role in ["branch_manager", "area_manager"]:
                    timer_key = f"{username}_{entry_id}"
                    if timer_key not in st.session_state.insurance_open_times:
                        st.session_state.insurance_open_times[timer_key] = time.time()

                    elapsed = time.time() - st.session_state.insurance_open_times[timer_key]
                    remaining = max(0, 10 - int(elapsed))

                    if remaining > 0:
                        st.markdown(
                            f'<div class="timer-message">⏳ Please review the application carefully. Action buttons will be available in {remaining} seconds...</div>',
                            unsafe_allow_html=True
                        )
                        time.sleep(1)
                        st.rerun()

                col_approve, col_reject = st.columns(2)

                with col_approve:
                    if st.button(f"✅ Approve", key=f"approve_{entry_id}", type="primary", use_container_width=True):
                        for i, e in enumerate(db_fresh["insurance_entries"]):
                            if e.get("entry_id") == entry_id:
                                if role == "branch_manager":
                                    db_fresh["insurance_entries"][i]["status"] = "approved_by_branch_manager"
                                    db_fresh["insurance_entries"][i]["approved_by_bm"] = username
                                    db_fresh["insurance_entries"][i]["bm_approval_time"] = datetime.now().strftime(
                                        "%Y-%m-%d %H:%M:%S")
                                elif role == "area_manager":
                                    db_fresh["insurance_entries"][i]["status"] = "approved_by_area_manager"
                                    db_fresh["insurance_entries"][i]["approved_by_am"] = username
                                    db_fresh["insurance_entries"][i]["am_approval_time"] = datetime.now().strftime(
                                        "%Y-%m-%d %H:%M:%S")
                                elif role == "AGM":
                                    db_fresh["insurance_entries"][i]["status"] = "approved_by_agm"
                                    db_fresh["insurance_entries"][i]["approved_by_agm"] = username
                                    db_fresh["insurance_entries"][i]["agm_approval_time"] = datetime.now().strftime(
                                        "%Y-%m-%d %H:%M:%S")
                                break

                        if save_data(db_fresh):
                            timer_key = f"{username}_{entry_id}"
                            if timer_key in st.session_state.insurance_open_times:
                                del st.session_state.insurance_open_times[timer_key]
                            st.success("✅ Application approved successfully!")
                            time.sleep(1)
                            st.rerun()

                with col_reject:
                    reject_key = f"reject_reason_{entry_id}"
                    show_reject_key = f"show_reject_{entry_id}"

                    if st.session_state.get(show_reject_key, False):
                        reason = st.text_area("Rejection Reason *", key=reject_key,
                                              placeholder="Enter reason for rejection")

                        col_confirm, col_cancel = st.columns(2)
                        with col_confirm:
                            if st.button("Confirm Reject", key=f"confirm_reject_{entry_id}", type="primary"):
                                if reason:
                                    for i, e in enumerate(db_fresh["insurance_entries"]):
                                        if e.get("entry_id") == entry_id:
                                            db_fresh["insurance_entries"][i]["status"] = "rejected"
                                            db_fresh["insurance_entries"][i]["rejection_reason"] = reason
                                            break

                                    if save_data(db_fresh):
                                        timer_key = f"{username}_{entry_id}"
                                        if timer_key in st.session_state.insurance_open_times:
                                            del st.session_state.insurance_open_times[timer_key]
                                        st.session_state[show_reject_key] = False
                                        st.success("Application rejected.")
                                        time.sleep(1)
                                        st.rerun()
                                else:
                                    st.error("Rejection reason is required")

                        with col_cancel:
                            if st.button("Cancel", key=f"cancel_reject_{entry_id}"):
                                st.session_state[show_reject_key] = False
                                st.rerun()
                    else:
                        if st.button(f"❌ Reject", key=f"reject_{entry_id}", use_container_width=True):
                            st.session_state[show_reject_key] = True
                            st.rerun()


# [Keep all other existing functions EXACTLY as they are - no changes]
# ====================
# MANAGE CUSTOMER MAIN PAGE
# ====================
def manage_customer_main(user):
    """Main manage customer page"""
    st.markdown(f'<h2 class="burgundy-header">📋 Manage Customer</h2>', unsafe_allow_html=True)

    st.markdown(f'''
    <div class="clean-card">
        <h3>Welcome, {user.get("username")}!</h3>
        <p>Select an action below to manage your customer leads or insurance applications:</p>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<div style="margin:2rem 0;"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📝 Lead Entry", use_container_width=True, type="primary"):
            st.session_state.manage_customer_page = "lead_entry"
            st.rerun()

    with col2:
        if st.button("📊 Lead Status", use_container_width=True, type="primary"):
            st.session_state.manage_customer_page = "lead_status"
            st.rerun()

    with col3:
        if st.button("🏥 Insurance Application", use_container_width=True, type="primary"):
            st.session_state.manage_customer_page = "insurance_application"
            st.rerun()

# ====================
# LEAD ENTRY PAGE (CONTINUED & BALANCED)
# ====================
def lead_entry_page(user, db_local):
    """Lead entry form with GPS location"""
    st.markdown(f'<h2 class="burgundy-header">📝 Lead Entry</h2>', unsafe_allow_html=True)

    if st.button("← Back", use_container_width=False):
        st.session_state.manage_customer_page = "main"
        st.rerun()

    st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)

    # AUTO-FILLED SECTION
    staff_name = user.get("username")
    branch = user.get("assigned_branches", [""])[0] if user.get("assigned_branches") else "N/A"

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("👤 Staff Name", value=staff_name, disabled=True, key="staff_auto")

    with col2:
        st.text_input("🏢 Branch", value=branch, disabled=True, key="branch_auto")

    st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)

    # LOCATION SECTION
    st.markdown("### 📍 Location")

    col_btn, col_input = st.columns([1, 2])

    with col_btn:
        if st.button("📡 Capture GPS", use_container_width=True, type="primary", key="capture_gps"):
            st.session_state.show_gps = True

    with col_input:
        location_manual = st.text_input(
            "Manual Location",
            placeholder="Or enter location manually",
            key="manual_location_input"
        )

    location_final = None
    gps_lat = None
    gps_lon = None

    if st.session_state.show_gps:
        st.markdown('<div style="margin:0.5rem 0;"></div>', unsafe_allow_html=True)
        render_gps_component()

    if location_manual:
        location_final = location_manual

    st.markdown('<div style="margin:2rem 0;"></div>', unsafe_allow_html=True)

    # LEAD INFORMATION SECTION
    st.markdown("### 📋 Lead Information")

    with st.form(key="lead_entry_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            lead_type = st.selectbox(
                "🔥 Lead Type *",
                ["HOT", "WARM", "COOL"],
                key="lead_type"
            )

        with col2:
            customer_name = st.text_input(
                "👤 Customer Name *",
                placeholder="Enter name",
                key="customer_name"
            )

        with col3:
            phone = st.text_input(
                "📞 Phone Number *",
                placeholder="10 digit number",
                max_chars=10,
                key="phone"
            )

        st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            job = st.text_input(
                "💼 Job / Occupation *",
                placeholder="Enter occupation",
                key="job"
            )

        with col2:
            if user.get("department") == "Sales":
                assigned_products = user.get("assigned_products", [])
                if assigned_products:
                    product = st.selectbox(
                        "📦 Product *",
                        assigned_products,
                        key="product"
                    )
                else:
                    st.warning("⚠️ No products assigned. Contact your manager.")
                    product = None
            else:
                product = st.text_input(
                    "📦 Product *",
                    placeholder="Enter product",
                    key="product_text"
                )

        st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

        description = st.text_area(
            "📝 Description *",
            placeholder="Enter detailed lead description",
            height=120,
            key="description"
        )

        st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)

        submitted = st.form_submit_button("✅ Save Lead", use_container_width=True, type="primary")

        if submitted:
            if not phone.isdigit() or len(phone) != 10:
                st.error("❌ Phone number must be exactly 10 digits!")
            elif not all([customer_name, job, phone, product, description]):
                st.error("❌ All fields marked with (*) are required!")
            elif not location_final:
                st.error("❌ Location is required!")
            else:
                customer_leads = db_local.get("customer_leads", [])
                lead_id = generate_lead_id(customer_leads)

                if gps_lat and gps_lon:
                    map_url = f"https://www.google.com/maps?q={gps_lat},{gps_lon}"
                else:
                    map_url = f"https://www.google.com/maps/search/?api=1&query={location_final.replace(' ', '+')}"

                new_lead = {
                    "lead_id": lead_id,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "staff_name": staff_name,
                    "branch": branch,
                    "location": location_final,
                    "location_url": map_url,
                    "gps_lat": gps_lat,
                    "gps_lon": gps_lon,
                    "lead_type": lead_type,
                    "customer_name": customer_name,
                    "job": job,
                    "phone_number": phone,
                    "product": product,
                    "description": description,
                    "department": user.get("department", "Sales"),
                    "status": "active",
                    "last_followup": datetime.now().strftime("%Y-%m-%d"),
                    "followup_count": 0,
                    "converted": False,
                    "customer_id": None
                }

                customer_leads.append(new_lead)
                db_local["customer_leads"] = customer_leads

                if save_data(db_local):
                    st.success(f"✅ Lead {lead_id} saved successfully!")
                    st.balloons()
                    st.session_state.show_gps = False
                    st.session_state.gps_data = None
                    time.sleep(1)
                    st.rerun()

    # VIEW SAVED LEADS
    st.markdown('<div style="margin:2rem 0;"></div>', unsafe_allow_html=True)

    if st.button("📊 View Saved Leads", use_container_width=True, type="secondary"):
        st.session_state.show_saved_leads = not st.session_state.show_saved_leads
        st.rerun()

    if st.session_state.show_saved_leads:
        st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 Saved Leads")

        customer_leads = db_local.get("customer_leads", [])
        username = user.get("username")
        my_leads = [l for l in customer_leads if l.get("staff_name") == username]

        if not my_leads:
            st.info("No leads saved yet.")
        else:
            display_data = []
            for lead in my_leads:
                if lead.get("converted", False):
                    status_display = "Converted"
                else:
                    status_display = lead.get("status", "active").title()

                display_data.append({
                    "Lead ID": lead.get("lead_id"),
                    "Date": lead.get("timestamp", "").split(" ")[0],
                    "Customer": lead.get("customer_name"),
                    "Phone": lead.get("phone_number"),
                    "Type": lead.get("lead_type"),
                    "Product": lead.get("product"),
                    "Location": lead.get("location"),
                    "Status": status_display
                })

            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, height=300, hide_index=True)

            st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)

            # LOCATION VIEWER & DELETE SECTION
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("#### 📍 View Location on Map")
                lead_ids_with_names = [f"{l.get('lead_id')} - {l.get('customer_name')}" for l in my_leads]
                selected_display = st.selectbox("Select Lead", lead_ids_with_names, key="map_select")

                if selected_display:
                    selected_id = selected_display.split(" - ")[0]
                    selected_lead = next((l for l in my_leads if l.get("lead_id") == selected_id), None)

                    if selected_lead:
                        location_url = selected_lead.get("location_url", "")
                        location_text = selected_lead.get("location", "Unknown")

                        st.markdown(f"**Location:** {location_text}")

                        if st.button("🗺️ Open in Google Maps", use_container_width=True, type="secondary",
                                     key="open_map"):
                            st.markdown(f'<meta http-equiv="refresh" content="0; url={location_url}">',
                                        unsafe_allow_html=True)
                            st.markdown(f'[Click here if not redirected]({location_url})', unsafe_allow_html=True)

            with col2:
                st.markdown("#### 🗑️ Delete Lead")
                lead_ids = [l.get("lead_id") for l in my_leads]
                selected_delete_id = st.selectbox("Select Lead ID", lead_ids, key="delete_select")

                if st.button("🗑️ Delete", use_container_width=True, type="secondary", key="delete_lead_btn"):
                    if st.session_state.delete_confirm_lead != selected_delete_id:
                        st.session_state.delete_confirm_lead = selected_delete_id
                        st.warning(f"⚠️ Click delete again to confirm deletion of {selected_delete_id}")
                        st.rerun()
                    else:
                        updated_leads = [l for l in db_local["customer_leads"] if
                                         l.get("lead_id") != selected_delete_id]
                        db_local["customer_leads"] = updated_leads

                        if save_data(db_local):
                            st.success(f"✅ Lead {selected_delete_id} deleted!")
                            st.session_state.delete_confirm_lead = None
                            time.sleep(1)
                            st.rerun()


# ====================
# LEAD STATUS PAGE
# ====================
def lead_status_page(user, db_local):
    """Lead status tracking and follow-up page"""
    st.markdown(f'<h2 class="burgundy-header">📊 Lead Status</h2>', unsafe_allow_html=True)

    if st.button("← Back to Manage Customer"):
        st.session_state.manage_customer_page = "main"
        st.rerun()

    st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)

    customer_leads = db_local.get("customer_leads", [])
    username = user.get("username")
    my_leads = [l for l in customer_leads if l.get("staff_name") == username and not l.get("converted", False)]

    if not my_leads:
        st.info("No active leads found. Start by creating new leads in Lead Entry.")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total = len(my_leads)
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{total}</div><div class="metric-label">Total Leads</div></div>',
            unsafe_allow_html=True)

    with col2:
        hot = len([l for l in my_leads if l.get("lead_type") == "HOT"])
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{hot}</div><div class="metric-label">Hot Leads</div></div>',
            unsafe_allow_html=True)

    with col3:
        warm = len([l for l in my_leads if l.get("lead_type") == "WARM"])
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{warm}</div><div class="metric-label">Warm Leads</div></div>',
            unsafe_allow_html=True)

    with col4:
        cool = len([l for l in my_leads if l.get("lead_type") == "COOL"])
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{cool}</div><div class="metric-label">Cool Leads</div></div>',
            unsafe_allow_html=True)

    st.markdown('<div style="margin:2rem 0;"></div>', unsafe_allow_html=True)

    today = datetime.now().date()
    followup_leads = []

    for lead in my_leads:
        last_followup = datetime.strptime(lead.get("last_followup"), "%Y-%m-%d").date()
        days_since = (today - last_followup).days

        if days_since >= 15:
            followup_leads.append(lead)

    if followup_leads:
        st.markdown(f'''
        <div class="timer-message">
            ⏰ {len(followup_leads)} lead(s) require follow-up today (15+ days old)
        </div>
        ''', unsafe_allow_html=True)

        if st.button("📅 Show Follow-Up Today", use_container_width=True, type="primary"):
            st.session_state.show_followup = True
            st.rerun()

    st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)

    leads_to_show = followup_leads if st.session_state.get("show_followup", False) else my_leads

    if st.session_state.get("show_followup", False):
        st.markdown("### 📅 Follow-Up Required")
        if st.button("Show All Leads"):
            st.session_state.show_followup = False
            st.rerun()
    else:
        st.markdown("### 📋 All Active Leads")

    for lead in leads_to_show:
        lead_id = lead.get("lead_id")
        lead_type = lead.get("lead_type")

        badge_class = f"lead-badge-{lead_type.lower()}"

        with st.expander(f"{lead_id} | {lead.get('customer_name')} | {lead.get('phone_number')}"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"**Customer:** {lead.get('customer_name')}")
                st.markdown(f"**Phone:** {lead.get('phone_number')}")
                st.markdown(f"**Job:** {lead.get('job')}")

            with col2:
                st.markdown(f"**Product:** {lead.get('product')}")
                st.markdown(f"**Location:** {lead.get('location')}")
                st.markdown(f"**Branch:** {lead.get('branch')}")

            with col3:
                st.markdown(f'<div class="{badge_class}">🔥 {lead_type}</div>', unsafe_allow_html=True)
                st.markdown(f"**Last Follow-up:** {lead.get('last_followup')}")
                st.markdown(f"**Follow-ups:** {lead.get('followup_count', 0)}")

            st.markdown("---")
            st.markdown(f"**Description:** {lead.get('description')}")

            st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

            col_update, col_convert = st.columns(2)

            with col_update:
                with st.form(key=f"update_form_{lead_id}"):
                    st.markdown("#### 🔄 Update Lead")

                    new_lead_type = st.selectbox("Lead Type", ["HOT", "WARM", "COOL"],
                                                 index=["HOT", "WARM", "COOL"].index(lead_type),
                                                 key=f"type_{lead_id}")
                    new_description = st.text_area("Description", value=lead.get("description"),
                                                   key=f"desc_{lead_id}", height=100)

                    if st.form_submit_button("💾 Update", type="primary"):
                        for i, l in enumerate(db_local["customer_leads"]):
                            if l.get("lead_id") == lead_id:
                                db_local["customer_leads"][i]["lead_type"] = new_lead_type
                                db_local["customer_leads"][i]["description"] = new_description
                                db_local["customer_leads"][i]["last_followup"] = datetime.now().strftime("%Y-%m-%d")
                                db_local["customer_leads"][i]["followup_count"] = l.get("followup_count", 0) + 1
                                break

                        if save_data(db_local):
                            st.success("✅ Lead updated successfully!")
                            time.sleep(1)
                            st.rerun()

            with col_convert:
                st.markdown("#### ✅ Convert Lead")
                st.markdown('<div style="margin:0.5rem 0;"></div>', unsafe_allow_html=True)

                with st.form(key=f"convert_form_{lead_id}"):
                    customer_id = st.text_input("Enter Customer ID (numeric only)",
                                                placeholder="e.g., 12345",
                                                key=f"custid_{lead_id}")

                    if st.form_submit_button("🎯 Mark as Converted", type="primary"):
                        if customer_id and customer_id.isdigit():
                            for i, l in enumerate(db_local["customer_leads"]):
                                if l.get("lead_id") == lead_id:
                                    db_local["customer_leads"][i]["converted"] = True
                                    db_local["customer_leads"][i]["customer_id"] = customer_id
                                    db_local["customer_leads"][i]["conversion_date"] = datetime.now().strftime(
                                        "%Y-%m-%d %H:%M:%S")
                                    break

                            if save_data(db_local):
                                st.success(f"✅ Lead {lead_id} marked as converted with Customer ID: {customer_id}")
                                st.balloons()
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error("❌ Please enter a valid numeric Customer ID")


# ====================
# USER MANAGEMENT PAGE
# ====================
def user_management_page(user, db_local):
    """User management page for admins and managers"""
    role = user.get("role")
    if role not in ["admin", "AGM", "area_manager", "branch_manager"]:
        st.error("❌ Access Denied: You don't have permission to manage users.")
        st.info("ℹ️ This page is only accessible to Admin, AGM, Area Managers, and Branch Managers.")
        if st.button("← Go Back to Reports"):
            st.session_state.page = "reports"
            st.rerun()
        return

    st.markdown(f'<h2 class="burgundy-header">👥 User Management</h2>', unsafe_allow_html=True)

    username = user.get("username")

    if role == "admin":
        filtered_users = {k: v for k, v in db_local["users"].items()}
    elif role == "AGM":
        filtered_users = {k: v for k, v in db_local["users"].items()
                          if v.get("created_by") == username and v.get("role") == "area_manager"}
    elif role == "area_manager":
        filtered_users = {k: v for k, v in db_local["users"].items()
                          if v.get("created_by") == username and v.get("role") == "branch_manager"}
    elif role == "branch_manager":
        filtered_users = {k: v for k, v in db_local["users"].items()
                          if v.get("created_by") == username and v.get("role") == "branch_staff"}
    else:
        filtered_users = {}

    if not filtered_users:
        st.info("No users created yet.")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{len(filtered_users)}</div><div class="metric-label">Total Users</div></div>',
            unsafe_allow_html=True)

    with col2:
        admins = len([u for u in filtered_users.values() if u.get("role") == "admin"])
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{admins}</div><div class="metric-label">Admins</div></div>',
            unsafe_allow_html=True)

    with col3:
        managers = len([u for u in filtered_users.values() if "manager" in u.get("role", "")])
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{managers}</div><div class="metric-label">Managers</div></div>',
            unsafe_allow_html=True)

    with col4:
        staff = len([u for u in filtered_users.values() if u.get("role") == "branch_staff"])
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{staff}</div><div class="metric-label">Staff</div></div>',
            unsafe_allow_html=True)

    st.markdown('<div style="margin:2rem 0;"></div>', unsafe_allow_html=True)

    user_data = []
    for uname, udata in filtered_users.items():
        if uname == "ADMIN":
            continue

        products_display = ""
        if udata.get('department') == 'Sales' and udata.get('assigned_products'):
            products_display = ', '.join(udata.get('assigned_products', []))

        user_data.append({
            "Username": uname,
            "Role": udata.get('role', '').replace('_', ' ').title(),
            "Department": udata.get('department', 'N/A'),
            "Branches": ', '.join(udata.get('assigned_branches', [])) or 'None',
            "Products": products_display or 'N/A',
            "Created By": udata.get('created_by', 'N/A'),
            "Created At": udata.get('created_at', 'N/A')[:10]
        })

    if user_data:
        df = pd.DataFrame(user_data)
        st.dataframe(df, use_container_width=True, height=400)

    st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("### Edit Users")
    for uname, udata in filtered_users.items():
        if uname == "ADMIN":
            continue

        with st.expander(f"✏️ Edit: {uname}"):
            with st.form(key=f"edit_form_{uname}"):
                col1, col2 = st.columns(2)

                with col1:
                    new_password = st.text_input("New Password (leave blank to keep current)", type="password",
                                                 key=f"pwd_{uname}")

                with col2:
                    new_branches = st.text_input("Branches (comma-separated)",
                                                 value=", ".join(udata.get("assigned_branches", [])),
                                                 key=f"branches_{uname}")

                if udata.get("department") == "Sales":
                    new_products = st.text_input("Products (comma-separated)",
                                                 value=", ".join(udata.get("assigned_products", [])),
                                                 key=f"products_{uname}")
                else:
                    new_products = ""

                col_save, col_delete = st.columns(2)

                with col_save:
                    if st.form_submit_button("💾 Save Changes", type="primary"):
                        if new_password:
                            db_local["users"][uname]["password"] = hash_password(new_password)
                        db_local["users"][uname]["assigned_branches"] = [b.strip() for b in new_branches.split(",") if
                                                                         b.strip()]

                        if udata.get("department") == "Sales":
                            db_local["users"][uname]["assigned_products"] = [p.strip() for p in new_products.split(",")
                                                                             if p.strip()]

                        if save_data(db_local):
                            st.success("✅ User updated!")
                            time.sleep(1)
                            st.rerun()

                with col_delete:
                    if st.form_submit_button("🗑️ Delete User"):
                        del db_local["users"][uname]
                        if save_data(db_local):
                            st.success(f"✅ User {uname} deleted!")
                            time.sleep(1)
                            st.rerun()

# ====================
# CREATE USER PAGE - FIXED (Added AGM Investment Option)
# ====================
def create_user_page(user, db_local):
    """User creation page for authorized roles"""
    role = user.get("role")
    if role not in ["admin", "AGM", "area_manager", "branch_manager"]:
        st.error("❌ Access Denied: You don't have permission to create users.")
        st.info("ℹ️ This page is only accessible to Admin, AGM, Area Managers, and Branch Managers.")
        if st.button("← Go Back to Reports"):
            st.session_state.page = "reports"
            st.rerun()
        return

    st.markdown(f'<h2 class="burgundy-header">👥 Create New User</h2>', unsafe_allow_html=True)

    # ✅ Role options (no duplicate AGM)
    if role == "admin":
        role_options = ["AGM", "Area Manager", "Branch Manager", "Branch Staff"]
    elif role == "AGM":
        role_options = ["Area Manager"]
    elif role == "area_manager":
        role_options = ["Branch Manager"]
    elif role == "branch_manager":
        role_options = ["Branch Staff"]
    else:
        st.warning("You don't have permission to create users.")
        return

    col1, col2 = st.columns(2)

    with col1:
        selected_role = st.selectbox("Select Role", role_options, key="role_select")
        username = st.text_input("Username")

    with col2:
        password = st.text_input("Password", type="password")

        # ✅ Department logic: Admin can choose Investment directly
        if role == "admin":
            dept = st.selectbox(
                "Select Department",
                ["Sales", "Investment", "MFI", "Recovery", "Legal", "Insurance"],
                key="dept_select"
            )
        elif role in ["AGM", "area_manager", "branch_manager"]:
            dept = user.get("department", "Sales")
            st.text_input("Department", value=dept, disabled=True)
        else:
            dept = st.selectbox("Select Department", ["Sales", "MFI", "Recovery", "Legal", "Insurance"],
                                key="dept_select")

    branch_list = []

    if selected_role in ["Area Manager", "Branch Manager", "Branch Staff"]:
        if role == "area_manager" and selected_role == "Branch Manager":
            my_branches = user.get("assigned_branches", [])
            if my_branches:
                st.info(f"📍 Your Assigned Branches: {', '.join(my_branches)}")
                branch = st.selectbox("Select Branch for New Branch Manager", my_branches, key="branch_select")
                branch_list = [branch]
            else:
                st.warning("⚠️ No branches assigned to you. Contact your AGM.")
                return

        elif role == "branch_manager" and selected_role == "Branch Staff":
            my_branches = user.get("assigned_branches", [])
            if my_branches:
                st.info(f"📍 Your Assigned Branches: {', '.join(my_branches)}")
                branch = st.selectbox("Select Branch for New Staff Member", my_branches, key="branch_staff_select")
                branch_list = [branch]
            else:
                st.warning("⚠️ No branches assigned to you. Contact Area Manager.")
                return
        else:
            branches_input = st.text_input("Assign Branches (comma-separated, e.g., Branch A, Branch B)")
            if branches_input:
                branch_list = [b.strip() for b in branches_input.split(",") if b.strip()]

    product_list = []

    # ✅ Product assignment - Admin + Sales only
    if role == "admin" and dept == "Sales":
        st.markdown("### 📦 Product Assignment (Admin Only - Sales Department)")
        st.info("💡 Assign specific products this user can submit in customer leads")

        products_input = st.text_input(
            "Assign Products (comma-separated, e.g., Product A, Product B, Product C)",
            placeholder="Enter products separated by commas",
            key="products_input"
        )

        if products_input:
            product_list = [p.strip() for p in products_input.split(",") if p.strip()]
            st.success(f"✅ Assigned Products: {', '.join(product_list)}")

    elif role != "admin" and dept == "Sales":
        creator_products = user.get("assigned_products", [])
        if creator_products:
            product_list = creator_products
            st.info(f"📦 Products (inherited from your account): {', '.join(product_list)}")
        else:
            st.warning(" ")

    st.markdown('<div style="margin:1.25rem 0;"></div>', unsafe_allow_html=True)

    if st.button("✅ Create User", use_container_width=True, type="primary"):
        if not username or username in db_local["users"]:
            st.error("❌ Username required and must be unique.")
            return

        if len(password) < 6:
            st.error("❌ Password must be at least 6 characters.")
            return

        # Product requirement only for Sales department
        if role == "admin" and dept == "Sales" and not product_list:
            st.error("❌ Products are required for Sales department users.")
            return

        # ✅ Smart AGM Investment detection
        if selected_role == "AGM" and dept == "Investment":
            role_save = "AGM"
        else:
            role_mapping = {
                "AGM": "AGM",
                "Area Manager": "area_manager",
                "Branch Manager": "branch_manager",
                "Branch Staff": "branch_staff"
            }
            role_save = role_mapping[selected_role]

        db_local["users"][username] = {
            "username": username,
            "password": hash_password(password),
            "role": role_save,
            "department": dept,
            "assigned_branches": branch_list,
            "assigned_products": product_list if dept == "Sales" else [],
            "created_by": user["username"],
            "created_at": str(datetime.now())
        }

        if save_data(db_local):
            branch_text = f" with branches: {', '.join(branch_list)}" if branch_list else ""
            product_text = f" and products: {', '.join(product_list)}" if product_list else ""
            st.success(f"✅ {selected_role} '{username}' created successfully{branch_text}{product_text}!")
            time.sleep(1)
            st.rerun()

# ====================
# REPORTS PAGE - WITH ADVANCED DOWNLOAD FILTERS
# ====================
def reports_page(db_local):
    """Main reports and analytics dashboard - WITH DOWNLOAD FILTERS"""
    st.markdown(f'<h2 class="burgundy-header">📊 Reports & Analytics Dashboard</h2>', unsafe_allow_html=True)

    user = st.session_state.user
    role = user.get("role")
    username = user.get("username")

    # ✅ RELOAD DATA FOR REAL-TIME UPDATES
    db_fresh = load_data()

    # Get all data sources
    all_leads = db_fresh.get("leads", [])
    customer_leads = db_fresh.get("customer_leads", [])
    insurance_entries = db_fresh.get("insurance_entries", [])

    # ✅ FILTER DATA BY ROLE
    if role == "admin":
        filtered_leads = all_leads
        filtered_customer_leads = customer_leads
        filtered_insurance = insurance_entries
    elif role == "branch_staff":
        filtered_leads = [l for l in all_leads if l.get("submitted_by") == username]
        filtered_customer_leads = [l for l in customer_leads if l.get("staff_name") == username]
        filtered_insurance = [e for e in insurance_entries if e.get("staff_id") == username]
    elif role == "branch_manager":
        assigned_branches = user.get("assigned_branches", [])
        filtered_leads = [l for l in all_leads if l.get("branch") in assigned_branches]
        filtered_customer_leads = [l for l in customer_leads if l.get("branch") in assigned_branches]
        filtered_insurance = [e for e in insurance_entries if e.get("branch") in assigned_branches]
    elif role == "area_manager":
        assigned_branches = user.get("assigned_branches", [])
        filtered_leads = [l for l in all_leads if l.get("branch") in assigned_branches]
        filtered_customer_leads = [l for l in customer_leads if l.get("branch") in assigned_branches]
        filtered_insurance = [e for e in insurance_entries if e.get("branch") in assigned_branches]
    elif role == "AGM":
        ams = [u for u, d in db_fresh["users"].items()
               if d.get("created_by") == username and d.get("role") == "area_manager"]
        branches = []
        for am in ams:
            branches.extend(db_fresh["users"][am].get("assigned_branches", []))
        filtered_leads = [l for l in all_leads if l.get("branch") in branches]
        filtered_customer_leads = [l for l in customer_leads if l.get("branch") in branches]
        filtered_insurance = [e for e in insurance_entries if e.get("branch") in branches]
    else:
        filtered_leads = []
        filtered_customer_leads = []
        filtered_insurance = []

    # ===========================
    # SECTION 1: OVERVIEW METRICS
    # ===========================
    st.markdown("### 📈 Overview Metrics")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        total_leads = len(filtered_leads)
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{total_leads}</div><div class="metric-label">System Leads</div></div>',
            unsafe_allow_html=True)

    with col2:
        total_customer_leads = len(filtered_customer_leads)
        active_customer_leads = len([l for l in filtered_customer_leads if not l.get("converted", False)])
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{active_customer_leads}</div><div class="metric-label">Active Leads</div></div>',
            unsafe_allow_html=True)

    with col3:
        converted = len([l for l in filtered_customer_leads if l.get("converted", False)])
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{converted}</div><div class="metric-label">Converted</div></div>',
            unsafe_allow_html=True)

    with col4:
        total_insurance = len(filtered_insurance)
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{total_insurance}</div><div class="metric-label">Insurance Apps</div></div>',
            unsafe_allow_html=True)

    with col5:
        if role == "branch_manager":
            staff_count = len(
                set([l.get("submitted_by") or l.get("staff_name") for l in filtered_leads + filtered_customer_leads if
                     l.get("submitted_by") or l.get("staff_name")]))
            st.markdown(
                f'<div class="metric-card"><div class="metric-value">{staff_count}</div><div class="metric-label">Staff Members</div></div>',
                unsafe_allow_html=True)
        else:
            pending = len([l for l in filtered_leads if l.get("status") == "submitted"])
            st.markdown(
                f'<div class="metric-card"><div class="metric-value">{pending}</div><div class="metric-label">Pending</div></div>',
                unsafe_allow_html=True)

    st.markdown('<div style="margin:2.5rem 0;"></div>', unsafe_allow_html=True)

    # Credits FIN Dashboard
    credits_entries = db_fresh.get("credits_fin_entries", [])
    total_closing_amount = sum([e.get("amount", 0) for e in credits_entries])

    st.markdown("### 💰 Credits FIN Dashboard")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">₹{total_closing_amount / 100000:.1f}L</div><div class="metric-label">Total Closing Amount</div></div>',
            unsafe_allow_html=True)
    with col2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{len(credits_entries)}</div><div class="metric-label">Closed Accounts</div></div>',
            unsafe_allow_html=True)

    # ===========================
    # SECTION 2: STAFF BREAKDOWN (Branch Manager & Above)
    # ===========================
    if role in ["branch_manager", "area_manager", "AGM", "admin"]:
        st.markdown("### 👥 Staff Performance Breakdown")

        all_staff_data = {}

        for lead in filtered_leads:
            staff = lead.get("submitted_by", "Unknown")
            if staff not in all_staff_data:
                all_staff_data[staff] = {
                    "system_leads": 0,
                    "customer_leads": 0,
                    "insurance_apps": 0,
                    "converted": 0
                }
            all_staff_data[staff]["system_leads"] += 1

        for lead in filtered_customer_leads:
            staff = lead.get("staff_name", "Unknown")
            if staff not in all_staff_data:
                all_staff_data[staff] = {
                    "system_leads": 0,
                    "customer_leads": 0,
                    "insurance_apps": 0,
                    "converted": 0
                }
            all_staff_data[staff]["customer_leads"] += 1
            if lead.get("converted", False):
                all_staff_data[staff]["converted"] += 1

        for entry in filtered_insurance:
            staff = entry.get("staff_id", "Unknown")
            if staff not in all_staff_data:
                all_staff_data[staff] = {
                    "system_leads": 0,
                    "customer_leads": 0,
                    "insurance_apps": 0,
                    "converted": 0
                }
            all_staff_data[staff]["insurance_apps"] += 1

        if all_staff_data:
            staff_df_data = []
            for staff, data in all_staff_data.items():
                staff_df_data.append({
                    "Staff Name": staff,
                    "System Leads": data["system_leads"],
                    "Customer Leads": data["customer_leads"],
                    "Converted": data["converted"],
                    "Insurance Apps": data["insurance_apps"],
                    "Total Activity": data["system_leads"] + data["customer_leads"] + data["insurance_apps"]
                })

            staff_df = pd.DataFrame(staff_df_data)
            staff_df = staff_df.sort_values("Total Activity", ascending=False)

            st.dataframe(staff_df, use_container_width=True, height=300, hide_index=True)

        st.markdown('<div style="margin:2rem 0;"></div>', unsafe_allow_html=True)

    # ===========================
    # SECTION 3: CUSTOMER LEADS ANALYSIS
    # ===========================
    if filtered_customer_leads:
        st.markdown("### 📝 Customer Leads Analysis")

        col1, col2, col3 = st.columns(3)

        with col1:
            hot_leads = len(
                [l for l in filtered_customer_leads if l.get("lead_type") == "HOT" and not l.get("converted", False)])
            st.markdown(
                f'<div class="metric-card"><div class="metric-value">{hot_leads}</div><div class="metric-label">Hot Leads</div></div>',
                unsafe_allow_html=True)

        with col2:
            warm_leads = len(
                [l for l in filtered_customer_leads if l.get("lead_type") == "WARM" and not l.get("converted", False)])
            st.markdown(
                f'<div class="metric-card"><div class="metric-value">{warm_leads}</div><div class="metric-label">Warm Leads</div></div>',
                unsafe_allow_html=True)

        with col3:
            cool_leads = len(
                [l for l in filtered_customer_leads if l.get("lead_type") == "COOL" and not l.get("converted", False)])
            st.markdown(
                f'<div class="metric-card"><div class="metric-value">{cool_leads}</div><div class="metric-label">Cool Leads</div></div>',
                unsafe_allow_html=True)

        st.markdown('<div style="margin:2rem 0;"></div>', unsafe_allow_html=True)

    # ===========================
    # SECTION 4: INSURANCE STATUS OVERVIEW
    # ===========================
    if filtered_insurance:
        st.markdown("### 🏥 Insurance Applications Status")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            ins_pending = len([e for e in filtered_insurance if e.get("status") == "submitted"])
            st.markdown(
                f'<div class="metric-card"><div class="metric-value">{ins_pending}</div><div class="metric-label">Pending BM</div></div>',
                unsafe_allow_html=True)

        with col2:
            ins_bm_approved = len([e for e in filtered_insurance if e.get("status") == "approved_by_branch_manager"])
            st.markdown(
                f'<div class="metric-card"><div class="metric-value">{ins_bm_approved}</div><div class="metric-label">BM Approved</div></div>',
                unsafe_allow_html=True)

        with col3:
            ins_am_approved = len([e for e in filtered_insurance if e.get("status") == "approved_by_area_manager"])
            st.markdown(
                f'<div class="metric-card"><div class="metric-value">{ins_am_approved}</div><div class="metric-label">AM Approved</div></div>',
                unsafe_allow_html=True)

        with col4:
            ins_fully_approved = len([e for e in filtered_insurance if e.get("status") == "approved_by_agm"])
            st.markdown(
                f'<div class="metric-card"><div class="metric-value">{ins_fully_approved}</div><div class="metric-label">Fully Approved</div></div>',
                unsafe_allow_html=True)

        st.markdown('<div style="margin:2rem 0;"></div>', unsafe_allow_html=True)

    # ===========================
    # SECTION 5: VISUAL CHARTS
    # ===========================
    st.markdown("### 📊 Visual Analytics")

    col1, col2 = st.columns(2)

    with col1:
        if filtered_leads or filtered_customer_leads or filtered_insurance:
            st.markdown("#### Branch Distribution")
            branch_counts = {}

            for l in filtered_leads:
                branch = l.get("branch", "Unassigned")
                branch_counts[branch] = branch_counts.get(branch, 0) + 1

            for l in filtered_customer_leads:
                branch = l.get("branch", "Unassigned")
                branch_counts[branch] = branch_counts.get(branch, 0) + 1

            for e in filtered_insurance:
                branch = e.get("branch", "Unassigned")
                branch_counts[branch] = branch_counts.get(branch, 0) + 1

            if branch_counts:
                fig, ax = plt.subplots(figsize=(8, 5), facecolor='white')
                ax.set_facecolor('white')
                bars = ax.bar(list(branch_counts.keys()), list(branch_counts.values()),
                              color=PRIMARY_COLOR, alpha=0.85, edgecolor='white', linewidth=2)
                ax.set_ylabel('Total Entries', fontsize=10, fontweight='600')
                ax.set_xlabel('Branch', fontsize=10, fontweight='600')
                ax.tick_params(axis="x", rotation=45, labelsize=9)
                ax.tick_params(axis="y", labelsize=9)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.grid(axis='y', alpha=0.2)

                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2., height,
                            f'{int(height)}',
                            ha='center', va='bottom', fontweight='600', fontsize=9)

                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("No data available for branch distribution")

    with col2:
        if filtered_customer_leads:
            st.markdown("#### Customer Lead Types")
            type_counts = {}
            for l in filtered_customer_leads:
                if not l.get("converted", False):
                    ltype = l.get("lead_type", "Unknown")
                    type_counts[ltype] = type_counts.get(ltype, 0) + 1

            if type_counts:
                fig, ax = plt.subplots(figsize=(8, 5), facecolor='white')
                ax.set_facecolor('white')
                colors_type = ['#dc2626', '#f59e0b', '#3b82f6']
                wedges, texts, autotexts = ax.pie(
                    list(type_counts.values()),
                    labels=list(type_counts.keys()),
                    autopct='%1.1f%%',
                    startangle=90,
                    colors=colors_type,
                    textprops={'fontsize': 10, 'weight': '600'}
                )
                for autotext in autotexts:
                    autotext.set_color('white')
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("No active customer leads")
        else:
            st.info("No customer leads data")

    st.markdown('<div style="margin:2.5rem 0;"></div>', unsafe_allow_html=True)

    # Second row of charts
    col1, col2 = st.columns(2)

    with col1:
        if filtered_insurance:
            st.markdown("#### Insurance Status Breakdown")
            ins_status_counts = {}
            for e in filtered_insurance:
                status = e.get("status", "submitted")
                status_label = STATUS_LABELS.get(status, (status, ""))[0]
                ins_status_counts[status_label] = ins_status_counts.get(status_label, 0) + 1

            if ins_status_counts:
                fig, ax = plt.subplots(figsize=(8, 5), facecolor='white')
                ax.set_facecolor('white')
                colors_ins = [INSURANCE_STATUS_COLORS.get(k, "#94a3b8") for k in
                              ["submitted", "approved_by_branch_manager", "approved_by_area_manager", "approved_by_agm",
                               "rejected"] if STATUS_LABELS.get(k, ("", ""))[0] in ins_status_counts]

                ax.barh(list(ins_status_counts.keys()), list(ins_status_counts.values()),
                        color=colors_ins, alpha=0.85, edgecolor='white', linewidth=2)
                ax.set_xlabel('Count', fontsize=10, fontweight='600')
                ax.tick_params(axis="both", labelsize=9)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.grid(axis='x', alpha=0.2)

                for i, v in enumerate(ins_status_counts.values()):
                    ax.text(v + 0.1, i, str(v), va='center', fontweight='600', fontsize=9)

                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("No insurance status data")
        else:
            st.info("No insurance applications")

    with col2:
        if role == "admin":
            st.markdown("#### Department Distribution")
            dept_counts = {}
            for l in all_leads:
                dept = l.get("department", "Unknown")
                dept_counts[dept] = dept_counts.get(dept, 0) + 1

            if dept_counts:
                fig, ax = plt.subplots(figsize=(8, 5), facecolor='white')
                ax.set_facecolor('white')
                bars = ax.barh(list(dept_counts.keys()), list(dept_counts.values()),
                               color=SECONDARY_COLOR, alpha=0.85, edgecolor='white', linewidth=2)
                ax.set_xlabel('Number of Leads', fontsize=10, fontweight='600')
                ax.tick_params(axis="both", labelsize=9)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.grid(axis='x', alpha=0.2)

                for i, v in enumerate(dept_counts.values()):
                    ax.text(v + 0.1, i, str(v), va='center', fontweight='600', fontsize=9)

                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("No department data")
        else:
            st.markdown("#### Lead Conversion Rate")
            if total_customer_leads > 0:
                conversion_rate = (converted / total_customer_leads) * 100

                fig, ax = plt.subplots(figsize=(8, 5), facecolor='white')
                ax.set_facecolor('white')

                categories = ['Converted', 'Active']
                values = [converted, active_customer_leads]
                colors_conv = ['#16a34a', '#f59e0b']

                bars = ax.bar(categories, values, color=colors_conv, alpha=0.85, edgecolor='white', linewidth=2)
                ax.set_ylabel('Count', fontsize=10, fontweight='600')
                ax.tick_params(axis="both", labelsize=9)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.grid(axis='y', alpha=0.2)

                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2., height,
                            f'{int(height)}',
                            ha='center', va='bottom', fontweight='600', fontsize=9)

                ax.text(0.5, max(values) * 0.9, f'Conversion Rate: {conversion_rate:.1f}%',
                        ha='center', fontsize=11, fontweight='700',
                        bbox=dict(boxstyle='round', facecolor='white', edgecolor=PRIMARY_COLOR, linewidth=2))

                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("No customer leads data")

    st.markdown('<div style="margin:2.5rem 0;"></div>', unsafe_allow_html=True)

    # ===========================
    # SECTION 6: RECENT ACTIVITY FEED
    # ===========================
    st.markdown("### 🕐 Recent Activity (Last 10 Entries)")

    recent_activities = []

    for lead in filtered_leads[:10]:
        recent_activities.append({
            "Timestamp": lead.get("timestamp", ""),
            "Type": "System Lead",
            "ID": lead.get("customer_id", "N/A"),
            "Name": lead.get("customer_name", "N/A"),
            "Staff": lead.get("submitted_by", "N/A"),
            "Branch": lead.get("branch", "N/A"),
            "Status": STATUS_LABELS.get(lead.get("status"), (lead.get("status"), ""))[0]
        })

    for lead in filtered_customer_leads[:10]:
        recent_activities.append({
            "Timestamp": lead.get("timestamp", ""),
            "Type": "Customer Lead",
            "ID": lead.get("lead_id", "N/A"),
            "Name": lead.get("customer_name", "N/A"),
            "Staff": lead.get("staff_name", "N/A"),
            "Branch": lead.get("branch", "N/A"),
            "Status": "Converted" if lead.get("converted", False) else "Active"
        })

    for entry in filtered_insurance[:10]:
        recent_activities.append({
            "Timestamp": entry.get("timestamp", ""),
            "Type": "Insurance",
            "ID": entry.get("entry_id", "N/A"),
            "Name": entry.get("applicant_name", "N/A"),
            "Staff": entry.get("staff_id", "N/A"),
            "Branch": entry.get("branch", "N/A"),
            "Status": STATUS_LABELS.get(entry.get("status"), (entry.get("status"), ""))[0]
        })

    recent_activities.sort(key=lambda x: x["Timestamp"], reverse=True)

    if recent_activities[:10]:
        activity_df = pd.DataFrame(recent_activities[:10])
        activity_df["Timestamp"] = pd.to_datetime(activity_df["Timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
        st.dataframe(activity_df, use_container_width=True, height=400, hide_index=True)
    else:
        st.info("No recent activities")

    st.markdown('<div style="margin:3rem 0;"></div>', unsafe_allow_html=True)

    # ===========================
    # ✅ SECTION 7: ADVANCED DOWNLOAD FILTERS
    # ===========================
    st.markdown("### 📥 Download Reports with Filters")

    st.markdown(f'''
    <div class="clean-card">
        <h4>Apply filters below and download customized reports</h4>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)

    # Create tabs for each data type
    tab1, tab2, tab3 = st.tabs(["📋 System Leads", "📝 Customer Leads", "🏥 Insurance Applications"])

    # ===========================
    # TAB 1: SYSTEM LEADS FILTERS
    # ===========================
    with tab1:
        st.markdown("#### Filter System Leads")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Branch filter
            all_branches = list(set([l.get("branch", "") for l in filtered_leads]))
            sys_branch_filter = st.selectbox("Branch", ["All"] + all_branches, key="sys_branch")

        with col2:
            # Department filter
            all_depts = list(set([l.get("department", "") for l in filtered_leads]))
            sys_dept_filter = st.selectbox("Department", ["All"] + all_depts, key="sys_dept")

        with col3:
            # Status filter
            sys_status_filter = st.selectbox("Status",
                                             ["All", "Submitted", "BM Approved", "AM Approved", "AGM Approved",
                                              "Rejected"], key="sys_status")

        with col4:
            # Staff filter (for managers)
            if role in ["branch_manager", "area_manager", "AGM", "admin"]:
                all_staff = list(set([l.get("submitted_by", "") for l in filtered_leads if l.get("submitted_by")]))
                sys_staff_filter = st.selectbox("Staff", ["All"] + all_staff, key="sys_staff")
            else:
                sys_staff_filter = "All"

        st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

        # Date range
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            sys_from_date = st.date_input("From Date", value=date.today() - timedelta(days=30), key="sys_from")

        with col2:
            sys_to_date = st.date_input("To Date", value=date.today(), key="sys_to")

        st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)

        # Apply filters
        sys_filtered = filtered_leads

        if sys_branch_filter != "All":
            sys_filtered = [l for l in sys_filtered if l.get("branch") == sys_branch_filter]

        if sys_dept_filter != "All":
            sys_filtered = [l for l in sys_filtered if l.get("department") == sys_dept_filter]

        if sys_status_filter != "All":
            status_mapping = {
                "Submitted": "submitted",
                "BM Approved": "approved_by_branch_manager",
                "AM Approved": "approved_by_area_manager",
                "AGM Approved": "approved_by_agm",
                "Rejected": "rejected"
            }
            sys_filtered = [l for l in sys_filtered if l.get("status") == status_mapping.get(sys_status_filter, "")]

        if sys_staff_filter != "All":
            sys_filtered = [l for l in sys_filtered if l.get("submitted_by") == sys_staff_filter]

        # Date filter
        sys_filtered = [l for l in sys_filtered if
                        sys_from_date <= datetime.strptime(l.get("timestamp", "2000-01-01 00:00:00"),
                                                           "%Y-%m-%d %H:%M:%S").date() <= sys_to_date]

        # Show count
        st.markdown(f"**📊 Filtered Results: {len(sys_filtered)} records**")

        # Download button
        if sys_filtered:
            excel_sys = export_to_excel(sys_filtered)
            st.download_button(
                label=f"📥 Download System Leads ({len(sys_filtered)} records)",
                data=excel_sys,
                file_name=f"system_leads_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )
        else:
            st.warning("No data to download with current filters")

    # ===========================
    # TAB 2: CUSTOMER LEADS FILTERS
    # ===========================
    with tab2:
        st.markdown("#### Filter Customer Leads")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Branch filter
            cust_branches = list(set([l.get("branch", "") for l in filtered_customer_leads]))
            cust_branch_filter = st.selectbox("Branch", ["All"] + cust_branches, key="cust_branch")

        with col2:
            # Lead type filter
            cust_type_filter = st.selectbox("Lead Type", ["All", "HOT", "WARM", "COOL"], key="cust_type")

        with col3:
            # Conversion status
            cust_status_filter = st.selectbox("Status", ["All", "Active", "Converted"], key="cust_status")

        with col4:
            # Staff filter (for managers)
            if role in ["branch_manager", "area_manager", "AGM", "admin"]:
                cust_staff = list(
                    set([l.get("staff_name", "") for l in filtered_customer_leads if l.get("staff_name")]))
                cust_staff_filter = st.selectbox("Staff", ["All"] + cust_staff, key="cust_staff")
            else:
                cust_staff_filter = "All"

        st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

        # Date range
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            cust_from_date = st.date_input("From Date", value=date.today() - timedelta(days=30), key="cust_from")

        with col2:
            cust_to_date = st.date_input("To Date", value=date.today(), key="cust_to")

        st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)

        # Apply filters
        cust_filtered = filtered_customer_leads

        if cust_branch_filter != "All":
            cust_filtered = [l for l in cust_filtered if l.get("branch") == cust_branch_filter]

        if cust_type_filter != "All":
            cust_filtered = [l for l in cust_filtered if l.get("lead_type") == cust_type_filter]

        if cust_status_filter == "Active":
            cust_filtered = [l for l in cust_filtered if not l.get("converted", False)]
        elif cust_status_filter == "Converted":
            cust_filtered = [l for l in cust_filtered if l.get("converted", False)]

        if cust_staff_filter != "All":
            cust_filtered = [l for l in cust_filtered if l.get("staff_name") == cust_staff_filter]

        # Date filter
        cust_filtered = [l for l in cust_filtered if
                         cust_from_date <= datetime.strptime(l.get("timestamp", "2000-01-01 00:00:00"),
                                                             "%Y-%m-%d %H:%M:%S").date() <= cust_to_date]

        # Show count
        st.markdown(f"**📊 Filtered Results: {len(cust_filtered)} records**")

        # Download button
        if cust_filtered:
            excel_cust = export_to_excel(cust_filtered)
            st.download_button(
                label=f"📥 Download Customer Leads ({len(cust_filtered)} records)",
                data=excel_cust,
                file_name=f"customer_leads_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )
        else:
            st.warning("No data to download with current filters")

    # ===========================
    # TAB 3: INSURANCE FILTERS
    # ===========================
    with tab3:
        st.markdown("#### Filter Insurance Applications")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Branch filter
            ins_branches = list(set([e.get("branch", "") for e in filtered_insurance]))
            ins_branch_filter = st.selectbox("Branch", ["All"] + ins_branches, key="ins_branch")

        with col2:
            # Insurance type filter
            ins_type_filter = st.selectbox("Insurance Type", ["All", "Health", "Hospitalization", "Vehicle"],
                                           key="ins_type")

        with col3:
            # Status filter
            ins_status_filter = st.selectbox("Status",
                                             ["All", "Submitted", "BM Approved", "AM Approved", "AGM Approved",
                                              "Rejected"], key="ins_status")

        with col4:
            # Staff filter (for managers)
            if role in ["branch_manager", "area_manager", "AGM", "admin"]:
                ins_staff = list(set([e.get("staff_id", "") for e in filtered_insurance if e.get("staff_id")]))
                ins_staff_filter = st.selectbox("Staff", ["All"] + ins_staff, key="ins_staff")
            else:
                ins_staff_filter = "All"

        st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

        # Date range & Customer ID search
        col1, col2, col3 = st.columns(3)

        with col1:
            ins_from_date = st.date_input("From Date", value=date.today() - timedelta(days=30), key="ins_from")

        with col2:
            ins_to_date = st.date_input("To Date", value=date.today(), key="ins_to")

        with col3:
            ins_customer_id = st.text_input("Customer ID (optional)", placeholder="e.g., INSC-00001", key="ins_cust_id")

        st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)

        # Apply filters
        ins_filtered = filtered_insurance

        if ins_branch_filter != "All":
            ins_filtered = [e for e in ins_filtered if e.get("branch") == ins_branch_filter]

        if ins_type_filter != "All":
            ins_filtered = [e for e in ins_filtered if e.get("insurance_type") == ins_type_filter]

        if ins_status_filter != "All":
            status_mapping = {
                "Submitted": "submitted",
                "BM Approved": "approved_by_branch_manager",
                "AM Approved": "approved_by_area_manager",
                "AGM Approved": "approved_by_agm",
                "Rejected": "rejected"
            }
            ins_filtered = [e for e in ins_filtered if e.get("status") == status_mapping.get(ins_status_filter, "")]

        if ins_staff_filter != "All":
            ins_filtered = [e for e in ins_filtered if e.get("staff_id") == ins_staff_filter]

        # Customer ID search
        if ins_customer_id:
            ins_filtered = [e for e in ins_filtered if e.get("customer_id", "").lower() == ins_customer_id.lower()]

        # Date filter
        ins_filtered = [e for e in ins_filtered if
                        ins_from_date <= datetime.strptime(e.get("timestamp", "2000-01-01 00:00:00"),
                                                           "%Y-%m-%d %H:%M:%S").date() <= ins_to_date]

        # Show count
        st.markdown(f"**📊 Filtered Results: {len(ins_filtered)} records**")

        # Download button
        if ins_filtered:
            excel_ins = export_insurance_to_excel(ins_filtered)
            st.download_button(
                label=f"📥 Download Insurance Applications ({len(ins_filtered)} records)",
                data=excel_ins,
                file_name=f"insurance_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )
        else:
            st.warning("No data to download with current filters")


# ====================
# CUSTOMER INQUIRY PAGE
# ====================
def customer_inquiry_page(user, db_local):
    """Customer inquiry and search page"""
    st.markdown(f'<h2 class="burgundy-header">🔍 Customer Inquiry</h2>', unsafe_allow_html=True)

    # ✅ RELOAD DATA FOR REAL-TIME UPDATES
    db_fresh = load_data()
    leads = db_fresh.get("leads", [])
    is_admin = user.get("role") == "admin"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        all_branches = list(set([l.get("branch", "") for l in leads]))
        branch_filter = st.selectbox("Filter by Branch", ["All"] + all_branches, key="inquiry_branch")

    with col2:
        all_depts = list(set([l.get("department", "") for l in leads]))
        dept_filter = st.selectbox("Filter by Department", ["All"] + all_depts, key="inquiry_dept")

    with col3:
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Approved"], key="inquiry_status")

    with col4:
        st.write("")

    st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

    col_date1, col_date2, col_spacer = st.columns([1, 1, 2])

    with col_date1:
        default_from = date.today() - timedelta(days=30)
        from_date = st.date_input("📅 From Date", value=default_from, key="from_date")

    with col_date2:
        default_to = date.today()
        to_date = st.date_input("📅 To Date", value=default_to, key="to_date")

    filtered = leads

    if branch_filter != "All":
        filtered = [l for l in filtered if l.get("branch") == branch_filter]

    if dept_filter != "All":
        filtered = [l for l in filtered if l.get("department") == dept_filter]

    if status_filter == "Pending":
        filtered = [l for l in filtered if l.get("status") == "submitted"]
    elif status_filter == "Approved":
        filtered = [l for l in filtered if "approved" in l.get("status", "")]

    if from_date and to_date:
        filtered = [l for l in filtered if
                    from_date <= datetime.strptime(l.get("timestamp", "2000-01-01 00:00:00"),
                                                   "%Y-%m-%d %H:%M:%S").date() <= to_date]

    st.markdown(
        f'<p style="margin:1.25rem 0;">Found <strong>{len(filtered)}</strong> records between <strong>{from_date}</strong> and <strong>{to_date}</strong></p>',
        unsafe_allow_html=True)

    if filtered:
        excel_data = export_to_excel(filtered)
        st.download_button(
            label="📥 Export to Excel",
            data=excel_data,
            file_name=f"inquiry_{from_date}_to_{to_date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

        st.markdown("### 📋 Customer Entries")
        display_data = []
        for l in filtered[:50]:
            display_data.append({
                "ID": l.get("customer_id"),
                "Name": l.get("customer_name"),
                "Phone": l.get("phone_number"),
                "Branch": l.get("branch"),
                "Dept": l.get("department", "N/A"),
                "Status": STATUS_LABELS.get(l.get("status"), (l.get("status"), ""))[0],
                "Date": l.get("timestamp", "").split(" ")[0]
            })

        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, height=400)


# ====================
# ACTIVITIES PAGE
# ====================
def activities_page(user, db_local):
    """Activities tracking page with approval workflow"""
    st.markdown(f'<h2 class="burgundy-header">📋 Activities</h2>', unsafe_allow_html=True)

    # ✅ RELOAD DATA FOR REAL-TIME UPDATES
    db_fresh = load_data()
    leads = db_fresh.get("leads", [])
    role = user.get("role")
    username = user.get("username")

    if role == "branch_staff":
        my_leads = [l for l in leads if l.get("submitted_by") == username]
    elif role == "branch_manager":
        my_leads = [l for l in leads if l.get("branch") in user.get("assigned_branches", [])]
    elif role == "area_manager":
        my_leads = [l for l in leads if l.get("branch") in user.get("assigned_branches", [])]
    elif role == "AGM":
        ams = [u for u, d in db_fresh["users"].items() if
               d.get("created_by") == username and d.get("role") == "area_manager"]
        branches = []
        for am in ams:
            branches.extend(db_fresh["users"][am].get("assigned_branches", []))
        my_leads = [l for l in leads if l.get("branch") in branches]
    else:
        my_leads = leads

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{len(my_leads)}</div><div class="metric-label">Total</div></div>',
            unsafe_allow_html=True)
    with col2:
        pending = len([l for l in my_leads if l.get("status") == "submitted"])
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{pending}</div><div class="metric-label">Pending</div></div>',
            unsafe_allow_html=True)
    with col3:
        approved = len([l for l in my_leads if "approved_by_agm" in l.get("status", "")])
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{approved}</div><div class="metric-label">Approved</div></div>',
            unsafe_allow_html=True)

    st.markdown('<div style="margin:1.25rem 0;"></div>', unsafe_allow_html=True)

    if my_leads:
        excel_data = export_to_excel(my_leads)
        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name=f"activities_{username}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.markdown('<div style="margin:1.25rem 0;"></div>', unsafe_allow_html=True)

    for idx, l in enumerate(my_leads[:20]):
        cid = l.get("customer_id", f"IDX-{idx}")
        status_label, status_color = STATUS_LABELS.get(l.get("status", ""), ("Unknown", "#94a3b8"))

        with st.expander(f"{cid} | {l.get('customer_name', 'N/A')} | {l.get('branch')}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Staff:** {l.get('staff_name')}")
                st.markdown(f"**Phone:** {l.get('phone_number')}")
            with col2:
                st.markdown(f"**Job:** {l.get('job')}")
                st.markdown(f"**Dept:** {l.get('department', 'N/A')}")
            with col3:
                st.markdown(
                    f'<div class="status-badge" style="background:{status_color};color:white;">{status_label}</div>',
                    unsafe_allow_html=True)

            if l.get("department") == "Insurance":
                current_status = l.get("status", "")

                lead_key = f"{username}_{cid}"
                if lead_key not in st.session_state.lead_open_times:
                    st.session_state.lead_open_times[lead_key] = time.time()

                elapsed = time.time() - st.session_state.lead_open_times[lead_key]
                remaining = max(0, 10 - int(elapsed))

                st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

                if remaining > 0:
                    st.markdown(
                        f'<div class="timer-message">⏳ Please review the details. Approval available in {remaining} seconds...</div>',
                        unsafe_allow_html=True
                    )
                    time.sleep(1)
                    st.rerun()
                else:
                    if role == "branch_manager" and current_status == "submitted":
                        if st.button("✅ Approve (Branch Manager)", key=f"bm_{cid}", type="primary"):
                            data = load_data()
                            for lead in data["leads"]:
                                if lead.get("customer_id") == cid:
                                    lead["status"] = "approved_by_branch_manager"
                                    break
                            save_data(data)
                            if lead_key in st.session_state.lead_open_times:
                                del st.session_state.lead_open_times[lead_key]
                            st.rerun()

                    elif role == "area_manager" and current_status == "approved_by_branch_manager":
                        if st.button("✅ Approve (Area Manager)", key=f"am_{cid}", type="primary"):
                            data = load_data()
                            for lead in data["leads"]:
                                if lead.get("customer_id") == cid:
                                    lead["status"] = "approved_by_area_manager"
                                    break
                            save_data(data)
                            if lead_key in st.session_state.lead_open_times:
                                del st.session_state.lead_open_times[lead_key]
                            st.rerun()

                    elif role == "AGM" and current_status == "approved_by_area_manager":
                        if st.button("✅ Approve (AGM)", key=f"agm_{cid}", type="primary"):
                            data = load_data()
                            for lead in data["leads"]:
                                if lead.get("customer_id") == cid:
                                    lead["status"] = "approved_by_agm"
                                    break
                            save_data(data)
                            if lead_key in st.session_state.lead_open_times:
                                del st.session_state.lead_open_times[lead_key]
                            st.rerun()


# ====================
# SETTINGS PAGE
# ====================
def settings_page(user, db_local):
    """Settings page for admin configuration"""
    if user.get("role") != "admin":
        st.error("❌ Access Denied: Only Admin can access settings.")
        if st.button("← Go Back to Reports"):
            st.session_state.page = "reports"
            st.rerun()
        return

    st.markdown(f'<h2 class="burgundy-header">⚙️ Settings</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        text = st.text_area("Dashboard Welcome Text", db_local.get("dashboard", {}).get("text", ""), height=150)
    with col2:
        img = st.file_uploader("Dashboard Image", type=["png", "jpg", "jpeg"])

        curr_img = db_local.get("dashboard", {}).get("image_path")
        if curr_img and os.path.exists(curr_img):
            st.image(curr_img, use_container_width=True)
            if st.button("🗑️ Delete Image"):
                try:
                    os.remove(curr_img)
                except:
                    pass
                db_local["dashboard"]["image_path"] = None
                save_data(db_local)
                st.rerun()

    st.markdown('<div style="margin:1.25rem 0;"></div>', unsafe_allow_html=True)

    if st.button("💾 Update Settings", use_container_width=True, type="primary"):
        db_local["dashboard"]["text"] = text
        if img:
            path = os.path.join(UPLOAD_DIR, f"dash_{int(datetime.now().timestamp())}.jpg")
            with open(path, "wb") as f:
                f.write(img.getbuffer())
            db_local["dashboard"]["image_path"] = path
        if save_data(db_local):
            st.success("✅ Settings updated!")
            time.sleep(1)
            st.rerun()


# ====================
# MAIN DASHBOARD - COMPLETE FIXED VERSION
# ====================
def dashboard():
    """Main dashboard with navigation"""
    user = st.session_state.user
    db_local = load_data()
    role = user.get("role")

    # SIDEBAR NAVIGATION
    with st.sidebar:
        st.markdown(f'<h1>📊 Menu</h1>', unsafe_allow_html=True)

        # ===========================
        # UNIVERSAL NAVIGATION
        # ===========================
        if st.button("📊 Reports", key="nav_reports", use_container_width=True):
            st.session_state.page = "reports"
            st.rerun()

        if st.button("🔍 Customer Inquiry", key="nav_inquiry", use_container_width=True):
            st.session_state.page = "inquiry"
            st.rerun()

        if st.button("📋 Activities", key="nav_activities", use_container_width=True):
            st.session_state.page = "activities"
            st.rerun()

        st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

        # ===========================
        # BRANCH STAFF NAVIGATION
        # ===========================
        if role == "branch_staff":
            st.markdown("### 📋 Branch Staff")
            if st.button("📋 Manage Customer", key="nav_manage_customer", use_container_width=True):
                st.session_state.page = "manage_customer"
                st.session_state.manage_customer_page = "main"
                st.rerun()

        # ===========================
        # MANAGER NAVIGATION (BM, AM, AGM)
        # ===========================
        if role in ["branch_manager", "area_manager", "AGM"]:
            st.markdown("### 👨‍💼 Functions")

            if st.button("🏥 Insurance Management", key="nav_insurance_mgmt", use_container_width=True):
                st.session_state.page = "insurance_management"
                st.rerun()

            if st.button("💰 RELIANT BEST", key="nav_reliant_best", use_container_width=True):
                st.session_state.page = "reliant_best"
                st.session_state.reliant_best_page = "main"
                st.rerun()
            if st.button("💰 CREDITSFIN LOG", key="nav_credits_fin", use_container_width=True):
                st.session_state.page = "credits_fin"
                st.session_state.credits_fin_page = "main"
                st.rerun()
            if user.get("department") == "Investment" and user.get("role") == "AGM":
                if st.button("💰 MANAGE CREDITS FIN", key="nav_manage_credits_fin", use_container_width=True):
                    st.session_state.page = "manage_credits_fin"
                    st.session_state.manage_credits_fin_page = "main"
                    st.rerun()

        # ===========================
        # ADMIN & MANAGER USER MANAGEMENT
        # ===========================
        if role in ["admin", "AGM", "area_manager", "branch_manager"]:
            st.markdown("### 👥 User Management")

            if st.button("👥 Create User", key="nav_create", use_container_width=True):
                st.session_state.page = "create_user"
                st.rerun()

            if st.button("👤 Manage Users", key="nav_manage", use_container_width=True):
                st.session_state.page = "manage_users"
                st.rerun()

        # ===========================
        # ADMIN ONLY FUNCTIONS
        # ===========================
        if role == "admin":
            st.markdown("### ⚙️ Administration")

            if st.button("⚙️ Settings", key="nav_settings", use_container_width=True):
                st.session_state.page = "settings"
                st.rerun()

        # ===========================
        # LOGOUT BUTTON
        # ===========================
        st.markdown('<div style="margin-top:3rem;"></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

        if st.button("🚪 LOGOUT", key="logout_sidebar", use_container_width=True, type="secondary"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.lead_open_times = {}
            st.session_state.insurance_open_times = {}
            st.session_state.delete_confirm = {}
            st.session_state.page = "reports"
            st.session_state.manage_customer_page = "main"
            st.session_state.insurance_page = "application"
            st.session_state.reliant_best_page = "main"
            st.session_state.gps_data = None
            st.session_state.show_gps = False
            st.session_state.show_insurance_entries = False
            st.session_state.show_saved_leads = False
            st.session_state.show_followup = False
            st.session_state.show_reliant_best_entries = False
            st.session_state.delete_confirm_lead = None
            st.rerun()

    # ===========================
    # USER INFO HEADER
    # ===========================
    st.markdown(f'''
        <div class="user-info-header">
            <span class="user-info">
                {user.get('username')} <span class="user-separator">|</span> {role.replace('_', ' ').title()}
            </span>
        </div>
    ''', unsafe_allow_html=True)

    # ===========================
    # PAGE ROUTING
    # ===========================
    page = st.session_state.get("page", "reports")

    if page == "reports":
        reports_page(db_local)

    elif page == "inquiry":
        customer_inquiry_page(user, db_local)

    elif page == "activities":
        activities_page(user, db_local)

    elif page == "create_user":
        create_user_page(user, db_local)

    elif page == "manage_users":
        user_management_page(user, db_local)

    elif page == "manage_customer":
        manage_page = st.session_state.get("manage_customer_page", "main")
        if manage_page == "main":
            manage_customer_main(user)
        elif manage_page == "lead_entry":
            lead_entry_page(user, db_local)
        elif manage_page == "lead_status":
            lead_status_page(user, db_local)
        elif manage_page == "insurance_application":
            insurance_application_page(user, db_local)

    elif page == "insurance_management":
        insurance_management_page(user, db_local)

    elif page == "reliant_best":
        reliant_page = st.session_state.get("reliant_best_page", "main")
        if reliant_page == "main":
            reliant_best_main(user)
        elif reliant_page == "entry":
            reliant_best_entry_page(user, db_local)
        elif reliant_page == "management":
            reliant_best_management_page(user, db_local)

    elif page == "settings":
        settings_page(user, db_local)

    elif page == "credits_fin":
        credits_page = st.session_state.get("credits_fin_page", "main")
        if credits_page == "main":
            credits_fin_main(user)
        elif credits_page == "fin_close":
            fin_close_page(user, db_local)
        elif credits_page == "place_bid":
            place_bid_page(user, db_local)

    elif page == "manage_credits_fin":
        manage_page = st.session_state.get("manage_credits_fin_page", "main")
        if manage_page == "main":
            manage_credits_fin_main(user)
        elif manage_page == "closed_accounts":
            closed_accounts_page(user, db_local)
        elif manage_page == "placed_bids":
            placed_bids_page(user, db_local)

    else:
        # Default page if invalid
        st.session_state.page = "reports"
        st.rerun()

def credits_fin_main(user):
    """Main CREDITSFIN LOG page for Branch Managers"""
    st.markdown(f'<h2 class="burgundy-header">💰 CREDITSFIN LOG</h2>', unsafe_allow_html=True)

    st.markdown(f'''
    <div class="clean-card">
        <h3>Welcome, {user.get("username")}!</h3>
        <p>Select an action below:</p>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<div style="margin:2rem 0;"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔒 FIN CLOSE", use_container_width=True, type="primary"):
            st.session_state.credits_fin_page = "fin_close"
            st.rerun()

    with col2:
        if st.button("📝 PLACE BID", use_container_width=True, type="primary"):
            st.session_state.credits_fin_page = "place_bid"
            st.rerun()


def fin_close_page(user, db_local):
    """FIN CLOSE page"""
    st.markdown(f'<h2 class="burgundy-header">🔒 FIN CLOSE</h2>', unsafe_allow_html=True)

    if st.button("← Back"):
        st.session_state.credits_fin_page = "main"
        st.rerun()

    # Constants
    branches = user.get("assigned_branches", [])
    branch = branches[0] if branches else "N/A"
    department = user.get("department", "N/A")
    user_name = user.get("username")

    st.markdown("### 📋 Constants")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("🏢 Branch Name", value=branch, disabled=True)
    with col2:
        st.text_input("📁 Department", value=department, disabled=True)
    with col3:
        st.text_input("👤 User Name", value=user_name, disabled=True)

    st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)

    with st.form(key="fin_close_form"):
        name = st.text_input("👤 Name *", key="name_input")

        customer_id = st.number_input(
            "🆔 Customer ID *", min_value=1, step=1, key="customer_id_input"
        )

        scheme = st.number_input(
            "🏷️ Scheme *",
            min_value=0.0,
            step=0.01,
            format="%.2f",
            help="Enter scheme number",
            key="scheme_input"
        )

        maturity = st.date_input("📅 Maturity *", key="maturity_input")

        amount = st.number_input(
            "💰 Amount *", min_value=0.0, step=0.01, key="amount_input"
        )

        narration = st.text_area("📝 Narration *", key="narration_input")

        submitted = st.form_submit_button(
            "✅ Save", use_container_width=True, type="primary"
        )

        if submitted:
            if not all([name, customer_id, maturity, amount, narration, scheme]):
                st.error("❌ All fields are required!")
            else:
                new_entry = {
                    "entry_id": generate_credits_fin_entry_id(db_local.get("credits_fin_entries", [])),
                    "branch": branch,
                    "department": department,
                    "user_name": user_name,
                    "name": name,
                    "customer_id": customer_id,
                    "scheme": scheme,  # ✅ Store scheme number
                    "maturity": str(maturity),
                    "amount": amount,
                    "narration": narration,
                    "booked": False,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                db_local["credits_fin_entries"].append(new_entry)
                save_data(db_local)
                st.success("✅ FIN Closed successfully!")
                st.balloons()
                st.stop()


def place_bid_page(user, db_local):
    """PLACE BID page - shows only unbooked FINs without approved bids"""
    st.markdown(f'<h2 class="burgundy-header">📝 PLACE BID</h2>', unsafe_allow_html=True)

    if st.button("← Back"):
        st.session_state.credits_fin_page = "main"
        st.rerun()

    db_fresh = load_data()
    all_entries = db_fresh.get("credits_fin_entries", [])
    all_bids = db_fresh.get("bids", [])

    if not all_entries:
        st.info("No closed FINs available.")
        return

    visible_entries = []
    for entry in all_entries:
        entry_id = entry.get("entry_id")

        if entry.get("booked", False):
            continue

        approved_bids = [b for b in all_bids if b.get("entry_id") == entry_id and b.get("status").upper() == "APPROVED"]
        if approved_bids:
            continue

        visible_entries.append(entry)

    if not visible_entries:
        st.info("✅ No slot available.")
        return

    for entry in visible_entries:
        with st.expander(f"{entry.get('entry_id')} | {entry.get('name')} | ₹{entry.get('amount'):,}"):
            st.markdown(f"**Branch:** {entry.get('branch')}")
            st.markdown(f"**Customer Name:** {entry.get('name')}")
            st.markdown(f"**Scheme:** {entry.get('scheme')}")  # ✅ FIXED - display correct scheme
            st.markdown(f"**Amount:** ₹{entry.get('amount'):,}")
            st.markdown(f"**Maturity:** {entry.get('maturity')}")

            if st.button("📝 Place Bid", key=f"bid_{entry.get('entry_id')}", use_container_width=True, type="primary"):
                try:
                    new_bid = {
                        "bid_id": generate_bid_id(db_fresh.get("bids", [])),
                        "entry_id": entry.get("entry_id"),
                        "bidder": user.get("username"),
                        "branch": entry.get("branch"),
                        "amount": entry.get("amount"),
                        "status": "PLACED",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    db_fresh["bids"].append(new_bid)
                    save_data(db_fresh)
                    st.success(f"✅ Bid placed successfully for {entry.get('entry_id')}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error placing bid: {e}")


def manage_credits_fin_main(user):
    """Main MANAGE CREDITS FIN page for AGM (Investment)"""
    if user.get("department") != "Investment" or user.get("role") != "AGM":
        st.error("❌ Access Denied")
        return

    st.markdown(f'<h2 class="burgundy-header">💰 MANAGE CREDITS FIN</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔒 CLOSED ACCOUNTS", use_container_width=True, type="primary"):
            st.session_state.manage_credits_fin_page = "closed_accounts"
            st.rerun()

    with col2:
        if st.button("📝 PLACED BIDS", use_container_width=True, type="primary"):
            st.session_state.manage_credits_fin_page = "placed_bids"
            st.rerun()


def export_credits_fin_to_excel(entries):
    """Convert list of dicts (entries) to Excel and return as BytesIO"""
    if not entries:
        return None

    df = pd.DataFrame(entries)

    columns_order = [
        "entry_id", "name", "customer_id", "branch", "department",
        "scheme", "amount", "booked", "narration", "timestamp", "user_name", "maturity"
    ]
    df = df[[c for c in columns_order if c in df.columns]]

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Closed Accounts")
    output.seek(0)
    return output


def closed_accounts_page(user, db_local):
    """CLOSED ACCOUNTS page"""
    st.markdown(f'<h2 class="burgundy-header">🔒 CLOSED ACCOUNTS</h2>', unsafe_allow_html=True)

    if st.button("← Back"):
        st.session_state.manage_credits_fin_page = "main"
        st.rerun()

    db_fresh = load_data()
    entries = filter_credits_fin_by_role(db_fresh.get("credits_fin_entries", []), user)

    st.markdown("### 🔍 Filters")
    col1, col2, col3 = st.columns(3)

    with col1:
        branch_options = ["All"] + list(set([e.get("branch") for e in entries]))
        branch_filter = st.selectbox("Branch", branch_options, key="closed_branch_filter")

    with col2:
        scheme_options = ["All"] + list(set([e.get("scheme") for e in entries]))
        scheme_filter = st.selectbox("Scheme (scheme)", scheme_options, key="closed_scheme_filter")

    with col3:
        status_options = ["All", "Booked", "Not Booked"]
        status_filter = st.selectbox("Status", status_options, key="closed_status_filter")

    filtered_entries = entries
    if branch_filter != "All":
        filtered_entries = [e for e in filtered_entries if e.get("branch") == branch_filter]
    if scheme_filter != "All":
        filtered_entries = [e for e in filtered_entries if e.get("scheme") == scheme_filter]
    if status_filter == "Booked":
        filtered_entries = [e for e in filtered_entries if e.get("booked", False)]
    elif status_filter == "Not Booked":
        filtered_entries = [e for e in filtered_entries if not e.get("booked", False)]

    if filtered_entries:
        excel_data = export_credits_fin_to_excel(filtered_entries)
        st.download_button(
            label="📥 Download Closed Accounts Excel",
            data=excel_data,
            file_name=f"closed_accounts_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    if not filtered_entries:
        st.info("No closed accounts match the filters.")
        return

    for entry in filtered_entries:
        booked_status = " (BOOKED)" if entry.get("booked", False) else ""

        with st.expander(f"{entry.get('entry_id')} | {entry.get('name')} | ₹{entry.get('amount'):,}{booked_status}"):
            st.markdown(f"**Branch:** {entry.get('branch')}")
            st.markdown(f"**Department:** {entry.get('department')}")
            st.markdown(f"**User Name:** {entry.get('user_name')}")
            st.markdown(f"**Scheme:** {entry.get('scheme')}")
            st.markdown(f"**Name:** {entry.get('name')}")
            st.markdown(f"**Customer ID:** {entry.get('customer_id')}")
            st.markdown(f"**Maturity:** {entry.get('maturity')}")
            st.markdown(f"**Amount:** ₹{entry.get('amount'):,}")
            st.markdown(f"**Narration:** {entry.get('narration')}")
            st.markdown(f"**Timestamp:** {entry.get('timestamp', '').split(' ')[0]}")

            if entry.get("booked"):
                st.success("✅ This account is BOOKED.")

            if user.get("role") == "AGM" and user.get("department") == "Investment":
                delete_key = f"delete_confirm_{entry.get('entry_id')}"
                st.markdown("---")
                col_book, col_delete, col_reject = st.columns([2, 1, 1])

                with col_book:
                    if entry.get("booked", False):
                        st.success("✅ Already BOOKED")
                    else:
                        if st.button(f"🔒 BOOKED", key=f"manual_book_{entry.get('entry_id')}"):
                            try:
                                db_fresh = load_data()
                                for e in db_fresh["credits_fin_entries"]:
                                    if e.get("entry_id") == entry.get("entry_id"):
                                        e["booked"] = True
                                for bid in db_fresh.get("bids", []):
                                    if bid.get("entry_id") == entry.get("entry_id"):
                                        bid["status"] = "BOOKED"
                                save_data(db_fresh)
                                st.success(f"✅ Account {entry['entry_id']} marked as BOOKED!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Failed to update booking: {e}")

                # ✅ NEW FEATURE: REJECT AFTER BOOKED (AGM)
                with col_reject:
                    if entry.get("booked", False):
                        if st.button("❌ Reject After Booked", key=f"reject_booked_{entry.get('entry_id')}"):
                            try:
                                db_fresh = load_data()
                                for e in db_fresh["credits_fin_entries"]:
                                    if e.get("entry_id") == entry.get("entry_id"):
                                        e["booked"] = False  # Unbook
                                for bid in db_fresh.get("bids", []):
                                    if bid.get("entry_id") == entry.get("entry_id"):
                                        bid["status"] = "PLACED"  # Revert bid status
                                save_data(db_fresh)
                                st.warning(f"⚠️ Booking rejected for Entry {entry.get('entry_id')} — returned to placed bids.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error rejecting booking: {e}")

                with col_delete:
                    if st.button(f"🗑️ Delete Entry", key=f"delete_{entry.get('entry_id')}"):
                        if st.session_state.get(delete_key, False):
                            try:
                                db_fresh = load_data()
                                db_fresh["credits_fin_entries"] = [
                                    e for e in db_fresh["credits_fin_entries"] if e.get("entry_id") != entry.get("entry_id")
                                ]
                                db_fresh["bids"] = [
                                    b for b in db_fresh["bids"] if b.get("entry_id") != entry.get("entry_id")
                                ]
                                save_data(db_fresh)
                                st.success(f"✅ Entry {entry.get('entry_id')} deleted successfully.")
                                st.session_state[delete_key] = False
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error during deletion: {e}")
                        else:
                            st.session_state[delete_key] = True
                            st.warning(f"⚠️ Click delete again to confirm deletion of Entry {entry.get('entry_id')}.")
                            st.rerun()


def placed_bids_page(user, db_local):
    """PLACED BIDS page with approval"""
    st.markdown(f'<h2 class="burgundy-header">📝 PLACED BIDS</h2>', unsafe_allow_html=True)

    if st.button("← Back"):
        st.session_state.manage_credits_fin_page = "main"
        st.rerun()

    db_fresh = load_data()
    bids = filter_bids_by_role(db_fresh.get("bids", []), user)

    for bid in bids:
        with st.expander(f"{bid.get('bid_id')} | {bid.get('bidder')} | ₹{bid.get('amount'):,}"):
            st.markdown(f"**Bidder:** {bid.get('bidder')}")
            st.markdown(f"**Entry ID:** {bid.get('entry_id')}")
            st.markdown(f"**Amount:** ₹{bid.get('amount'):,}")
            st.markdown(f"**Status:** {bid.get('status', '').upper()}")
            if bid.get("branch"):
                st.markdown(f"**Branch:** {bid.get('branch')}")

            if bid.get("status", "").upper() == "PLACED":
                col_approve, col_reject = st.columns(2)

                with col_approve:
                    if st.button("✅ Approve", key=f"approve_{bid.get('bid_id')}", type="primary"):
                        db_fresh = load_data()
                        for b in db_fresh["bids"]:
                            if b.get("bid_id") == bid.get("bid_id"):
                                b["status"] = "APPROVED"
                        for e in db_fresh["credits_fin_entries"]:
                            if e.get("entry_id") == bid.get("entry_id"):
                                e["booked"] = True
                        save_data(db_fresh)
                        st.success("✅ Bid approved! Account marked as BOOKED.")
                        st.rerun()

                with col_reject:
                    if st.button("❌ Reject", key=f"reject_{bid.get('bid_id')}", type="secondary"):
                        db_fresh = load_data()
                        for b in db_fresh["bids"]:
                            if b.get("bid_id") == bid.get("bid_id"):
                                b["status"] = "REJECTED"
                        save_data(db_fresh)
                        st.success("❌ Bid rejected.")
                        st.rerun()

# ====================
# MAIN ENTRY POINT
# ====================
def main():
    """Main application entry point"""
    if not st.session_state.logged_in:
        login_page()


    else:
        dashboard()

if __name__ == "__main__":
    main()
