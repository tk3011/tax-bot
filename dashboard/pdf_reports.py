import streamlit as st
from datetime import datetime

def show_pdf_reports(db, Receipt, Client):
    st.subheader("📄 Tax Reports")
    
    user_id = st.session_state.user_id
    clients = db.query(Client).filter(Client.user_id == user_id).all()
    
    if not clients:
        st.warning("No clients found")
        return
    
    selected_client = st.selectbox("Select Client", [c.name for c in clients])
    financial_year = st.selectbox("Financial Year", ["2024-2025", "2023-2024"])
    
    if st.button("Generate Report", type="primary"):
        report = f"Tax Report for {selected_client}\nFinancial Year: {financial_year}\nGenerated: {datetime.now()}"
        st.download_button("Download Report", report, f"report_{selected_client}.txt")
        st.balloons()
