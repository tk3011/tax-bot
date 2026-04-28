import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def show_activity_log(db):
    st.subheader("📋 Activity Log")
    st.markdown("*Track all actions performed in your practice*")
    
    # Sample activity data (in production, this comes from a database table)
    activities = [
        {"timestamp": datetime.now() - timedelta(minutes=5), "user": st.session_state.user_email, "action": "Added receipt", "client": "Client A", "details": "$45.00 - Officeworks"},
        {"timestamp": datetime.now() - timedelta(hours=1), "user": st.session_state.user_email, "action": "Added client", "client": "Client B", "details": "New client registered"},
        {"timestamp": datetime.now() - timedelta(hours=3), "user": st.session_state.user_email, "action": "Generated tax return", "client": "Client A", "details": "2024-2025 return"},
        {"timestamp": datetime.now() - timedelta(days=1), "user": st.session_state.user_email, "action": "Exported CSV", "client": "All clients", "details": "Tax data export"},
        {"timestamp": datetime.now() - timedelta(days=2), "user": st.session_state.user_email, "action": "BAS generated", "client": "Client A", "details": "Q2 2025 BAS"},
        {"timestamp": datetime.now() - timedelta(days=3), "user": st.session_state.user_email, "action": "Logged in", "client": "-", "details": "User logged in"},
    ]
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_filter = st.selectbox("Date Range", ["Today", "Last 7 days", "Last 30 days", "All time"])
    
    with col2:
        action_filter = st.multiselect("Action Type", ["Added receipt", "Added client", "Generated tax return", "Exported CSV", "BAS generated", "Logged in"])
    
    with col3:
        client_filter = st.text_input("Filter by client", placeholder="Client name")
    
    # Display activities
    st.divider()
    
    if activities:
        df = pd.DataFrame(activities)
        
        # Apply filters
        if date_filter == "Today":
            df = df[df['timestamp'] >= datetime.now().replace(hour=0, minute=0, second=0)]
        elif date_filter == "Last 7 days":
            df = df[df['timestamp'] >= datetime.now() - timedelta(days=7)]
        elif date_filter == "Last 30 days":
            df = df[df['timestamp'] >= datetime.now() - timedelta(days=30)]
        
        if action_filter:
            df = df[df['action'].isin(action_filter)]
        
        if client_filter:
            df = df[df['client'].str.contains(client_filter, case=False, na=False)]
        
        if len(df) > 0:
            for _, row in df.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 1.5, 2, 3])
                    with col1:
                        st.write(f"**{row['timestamp'].strftime('%d/%m/%Y %H:%M')}**")
                    with col2:
                        st.write(row['action'])
                    with col3:
                        st.write(row['client'])
                    with col4:
                        st.caption(row['details'])
                    st.divider()
        else:
            st.info("No activities match your filters")
        
        # Export
        if st.button("📥 Export Activity Log", use_container_width=True):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"activity_log_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No activities recorded yet")
    
    st.caption("🔒 All actions are logged for audit and compliance purposes")
