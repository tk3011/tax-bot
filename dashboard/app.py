import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db, Receipt, Client, User
from auth import require_auth

# Import modules with error handling
try:
    from receipt_scanner import show_receipt_scanner
except ImportError:
    def show_receipt_scanner(db, Receipt):
        st.info("Receipt scanner module loading...")

try:
    from portal_jockey import show_portal_jockey
except ImportError:
    def show_portal_jockey(db, Receipt, Client):
        st.info("ATO portal module loading...")

try:
    from tax_calculator import show_tax_return
except ImportError:
    def show_tax_return(db, Receipt, Client):
        st.info("Tax calculator module loading...")

try:
    from pdf_reports import show_pdf_reports
except ImportError:
    def show_pdf_reports(db, Receipt, Client):
        st.info("PDF reports module loading...")

try:
    from bas_generator import show_bas_generator
except ImportError:
    def show_bas_generator(db, Receipt, Client):
        st.info("BAS generator module loading...")

try:
    from compliance import show_compliance_dashboard
except ImportError:
    def show_compliance_dashboard(db, Client):
        st.info("Compliance module loading...")

try:
    from settings import show_settings
except ImportError:
    def show_settings(db):
        st.info("Settings module loading...")

try:
    from activity_log import show_activity_log
except ImportError:
    def show_activity_log(db):
        st.info("Activity log module loading...")

st.set_page_config(page_title="Tax Bot", page_icon="🤖", layout="wide")

# Check authentication
if not require_auth():
    st.stop()

st.title("🤖 Tax Bot - Complete Tax Agent Platform")
st.markdown(f"*Welcome back, {st.session_state.firm_name}!*")

st.sidebar.title("Menu")
page = st.sidebar.radio("Go to", [
    "Dashboard",
    "Receipt Scanner",
    "ATO Portal",
    "Tax Return",
    "BAS Generator",
    "Compliance",
    "PDF Reports",
    "Clients",
    "Activity Log",
    "Settings",
    "Export"
])

db = get_db()
user_id = st.session_state.user_id

if page == "Dashboard":
    st.subheader("📊 Practice Dashboard")
    
    receipts = db.query(Receipt).filter(Receipt.user_id == user_id).all()
    clients = db.query(Client).filter(Client.user_id == user_id).all()
    
    total_deductions = sum(r.amount for r in receipts)
    this_month = sum(1 for r in receipts if r.created_at >= datetime.now().replace(day=1))
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Receipts", len(receipts), delta=f"+{this_month} this month")
    col2.metric("Active Clients", len(clients))
    col3.metric("Total Deductions", f"${total_deductions:,.2f}")
    col4.metric("Time Saved", f"{len(receipts) * 5} mins")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Recent Receipts")
        if receipts:
            for r in receipts[-5:][::-1]:
                st.write(f"💰 ${r.amount:.2f} - {r.vendor} - {r.date}")
        else:
            st.info("No receipts yet")
    
    with col2:
        st.subheader("👥 Recent Clients")
        if clients:
            for c in clients[-5:][::-1]:
                st.write(f"👤 {c.name} - {c.email}")
        else:
            st.info("No clients yet")

elif page == "Receipt Scanner":
    show_receipt_scanner(db, Receipt)

elif page == "ATO Portal":
    show_portal_jockey(db, Receipt, Client)

elif page == "Tax Return":
    show_tax_return(db, Receipt, Client)

elif page == "BAS Generator":
    show_bas_generator(db, Receipt, Client)

elif page == "Compliance":
    show_compliance_dashboard(db, Client)

elif page == "PDF Reports":
    show_pdf_reports(db, Receipt, Client)

elif page == "Clients":
    st.subheader("👥 Client Management")
    
    tab1, tab2 = st.tabs(["Add Client", "All Clients"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name*")
            email = st.text_input("Email*")
            phone = st.text_input("Phone")
        with col2:
            tfn = st.text_input("TFN (9 digits)")
            abn = st.text_input("ABN (11 digits)")
            dob = st.date_input("Date of Birth", datetime.now() - timedelta(days=365*30))
        
        if st.button("💾 Save Client", type="primary"):
            if name and email:
                new_client = Client(
                    user_id=user_id,
                    name=name,
                    email=email,
                    tfn=tfn or "",
                    phone=phone or ""
                )
                db.add(new_client)
                db.commit()
                st.success(f"✅ Client {name} saved!")
                st.rerun()
            else:
                st.error("Name and email required")
    
    with tab2:
        all_clients = db.query(Client).filter(Client.user_id == user_id).all()
        if all_clients:
            for c in all_clients:
                with st.expander(f"👤 {c.name}"):
                    st.write(f"📧 {c.email}")
                    st.write(f"📞 {c.phone or 'Not provided'}")
                    st.write(f"🔢 TFN: {c.tfn or 'Not provided'}")
                    st.write(f"📅 Added: {c.created_at.strftime('%Y-%m-%d')}")
        else:
            st.info("No clients yet")

elif page == "Activity Log":
    show_activity_log(db)

elif page == "Settings":
    show_settings(db)

elif page == "Export":
    st.subheader("📤 Export Data")
    
    receipts = db.query(Receipt).filter(Receipt.user_id == user_id).all()
    
    if receipts:
        categories = {}
        for r in receipts:
            categories[r.category] = categories.get(r.category, 0) + r.amount
        
        st.subheader("📊 Summary by Category")
        for cat, amt in categories.items():
            st.write(f"{cat}: ${amt:.2f}")
        
        st.subheader(f"💰 Total Deductions: ${sum(r.amount for r in receipts):,.2f}")
        
        csv_data = "Date,Vendor,Amount,Category\n"
        for r in receipts:
            csv_data += f"{r.date},{r.vendor},{r.amount},{r.category}\n"
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📥 Download CSV", csv_data, "tax_data.csv", "text/csv")
        
        if st.button("🗑️ Delete All Data", type="secondary"):
            db.query(Receipt).filter(Receipt.user_id == user_id).delete()
            db.commit()
            st.warning("All data deleted!")
            st.rerun()
    else:
        st.info("No data to export")

db.close()
