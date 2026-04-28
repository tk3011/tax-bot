import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

def show_compliance_dashboard(db, Client):
    st.subheader("⚖️ Compliance Dashboard")
    st.markdown("*Track deadlines, renewals, and compliance requirements*")
    
    user_id = st.session_state.user_id
    clients = db.query(Client).filter(Client.user_id == user_id).all()
    
    today = datetime.now().date()
    
    # Sample deadlines (in production, these come from a database)
    deadlines = [
        {"task": "BAS Lodgment", "due_date": today + timedelta(days=5), "status": "Upcoming", "client": "All Clients"},
        {"task": "Superannuation Payment", "due_date": today + timedelta(days=12), "status": "Upcoming", "client": "All Clients"},
        {"task": "PAYG Withholding", "due_date": today + timedelta(days=20), "status": "Upcoming", "client": "All Clients"},
        {"task": "Annual Tax Return", "due_date": today + timedelta(days=45), "status": "Upcoming", "client": "All Clients"},
        {"task": "Professional Indemnity Renewal", "due_date": today - timedelta(days=10), "status": "Overdue", "client": "Admin"},
    ]
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    upcoming = len([d for d in deadlines if d["status"] == "Upcoming"])
    overdue = len([d for d in deadlines if d["status"] == "Overdue"])
    
    with col1:
        st.metric("Total Clients", len(clients))
    with col2:
        st.metric("Upcoming Deadlines", upcoming, delta="This month")
    with col3:
        st.metric("Overdue Items", overdue, delta="Action required", delta_color="inverse")
    with col4:
        compliance_rate = 100 - (overdue/(upcoming+overdue)*100 if upcoming+overdue>0 else 0)
        st.metric("Compliance Rate", f"{compliance_rate:.0f}%")
    
    st.divider()
    
    # Upcoming Deadlines
    st.subheader("📅 Upcoming Deadlines")
    
    upcoming_items = [d for d in deadlines if d["status"] == "Upcoming"]
    if upcoming_items:
        for d in upcoming_items:
            days_left = (d["due_date"] - today).days
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1:
                st.write(f"**{d['task']}**")
            with col2:
                st.write(f"Due: {d['due_date'].strftime('%d/%m/%Y')}")
            with col3:
                if days_left <= 7:
                    st.warning(f"{days_left} days left")
                else:
                    st.info(f"{days_left} days left")
            with col4:
                st.caption(d['client'])
    else:
        st.success("✅ No upcoming deadlines!")
    
    # Overdue Items
    overdue_items = [d for d in deadlines if d["status"] == "Overdue"]
    if overdue_items:
        st.subheader("⚠️ Overdue Items")
        for d in overdue_items:
            days_overdue = (today - d["due_date"]).days
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1:
                st.write(f"**{d['task']}**")
            with col2:
                st.write(f"Due: {d['due_date'].strftime('%d/%m/%Y')}")
            with col3:
                st.error(f"{days_overdue} days overdue")
            with col4:
                st.caption(d['client'])
    
    # ATO Requirements
    st.divider()
    st.subheader("🔐 ATO Compliance Requirements")
    
    requirements = [
        {"requirement": "DSP Registration", "status": "Pending", "status_color": "warning", "due_date": "31 Dec 2025"},
        {"requirement": "TLS 1.3 Compliance", "status": "Compliant", "status_color": "success", "due_date": "31 Jan 2026"},
        {"requirement": "Software ID Notification", "status": "Not Started", "status_color": "error", "due_date": "30 Jun 2026"},
        {"requirement": "Professional Indemnity Insurance", "status": "Active", "status_color": "success", "due_date": "30 Sep 2025"},
        {"requirement": "CPE Hours (2025)", "status": "In Progress", "status_color": "warning", "due_date": "31 Dec 2025"},
    ]
    
    for req in requirements:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(req["requirement"])
        with col2:
            if req["status_color"] == "success":
                st.success(req["status"])
            elif req["status_color"] == "warning":
                st.warning(req["status"])
            else:
                st.error(req["status"])
        with col3:
            st.caption(f"Due: {req['due_date']}")
    
    # Actions
    st.divider()
    st.subheader("📋 Recommended Actions")
    
    actions = [
        "📄 Register as Digital Service Provider (DSP) with ATO",
        "🔧 Update software to TLS 1.3 before January 2026",
        "📊 Complete 20 hours of CPE for 2025",
        "🔄 Renew Professional Indemnity insurance before expiry",
        "📝 Submit Software ID to ATO Access Manager"
    ]
    
    selected_actions = []
    for action in actions:
        if st.checkbox(action, key=action[:20]):
            selected_actions.append(action)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Generate Compliance Report", type="primary", use_container_width=True):
            report = f"""COMPLIANCE REPORT
Generated: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Firm: {st.session_state.firm_name}
Agent: {st.session_state.user_email}

CLIENT STATISTICS
Total Clients: {len(clients)}
Upcoming Deadlines: {upcoming}
Overdue Items: {overdue}
Compliance Rate: {compliance_rate:.0f}%

DEADLINES
"""
            for d in upcoming_items:
                report += f"- {d['task']}: {d['due_date'].strftime('%d/%m/%Y')} ({d['client']})\n"
            
            if overdue_items:
                report += f"\nOVERDUE ITEMS\n"
                for d in overdue_items:
                    report += f"- {d['task']}: {d['due_date'].strftime('%d/%m/%Y')} ({d['client']})\n"
            
            report += f"\nATO REQUIREMENTS\n"
            for req in requirements:
                report += f"- {req['requirement']}: {req['status']} (Due: {req['due_date']})\n"
            
            if selected_actions:
                report += f"\nSELECTED ACTIONS\n"
                for action in selected_actions:
                    report += f"- {action}\n"
            
            st.download_button(
                label="📥 Download Report",
                data=report,
                file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d')}.txt",
                key="download_compliance"
            )
            st.balloons()
    
    with col2:
        st.caption("💡 Mark actions as complete to track your progress")
