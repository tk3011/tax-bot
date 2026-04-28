import streamlit as st
from datetime import datetime

def show_activity_log(db):
    st.subheader("📋 Activity Log")
    
    st.info("Recent activities will appear here")
    
    # Sample activities
    activities = [
        "Added receipt - $45.00 at Officeworks",
        "Added new client - John Smith",
        "Generated tax return",
    ]
    
    for activity in activities:
        st.write(f"• {activity}")
    
    st.caption("Full activity logging coming soon")
