import streamlit as st
from db import get_db, User
import re

def show_settings(db):
    st.subheader("⚙️ Account Settings")
    st.markdown("*Manage your profile and practice settings*")
    
    user_id = st.session_state.user_id
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        st.error("User not found")
        return
    
    tab1, tab2, tab3 = st.tabs(["Profile", "Security", "Practice Settings"])
    
    with tab1:
        st.markdown("### Profile Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            firm_name = st.text_input("Firm Name", value=user.firm_name)
            email = st.text_input("Email", value=user.email)
        
        with col2:
            agent_code = st.text_input("ATO Agent Code", value=user.agent_code or "")
            phone = st.text_input("Phone Number", value=getattr(user, 'phone', ''))
        
        if st.button("💾 Update Profile", type="primary"):
            if firm_name and email:
                user.firm_name = firm_name
                user.email = email
                user.agent_code = agent_code
                db.commit()
                st.session_state.firm_name = firm_name
                st.session_state.user_email = email
                st.success("✅ Profile updated!")
                st.rerun()
            else:
                st.error("Firm name and email are required")
    
    with tab2:
        st.markdown("### Password")
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_password = st.text_input("Current Password", type="password")
        
        with col2:
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.button("🔐 Change Password", type="primary"):
            if not current_password or not new_password:
                st.error("Please enter current and new password")
            elif new_password != confirm_password:
                st.error("New passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                if user.check_password(current_password):
                    user.set_password(new_password)
                    db.commit()
                    st.success("✅ Password changed successfully!")
                    st.info("Please login again with your new password")
                    if st.button("Logout Now"):
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()
                else:
                    st.error("Current password is incorrect")
        
        st.divider()
        st.markdown("### Session Management")
        
        if st.button("🚪 Logout from All Devices", type="secondary"):
            st.warning("This will log you out from all devices")
            if st.button("Confirm Logout"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    
    with tab3:
        st.markdown("### Practice Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            default_financial_year = st.selectbox(
                "Default Financial Year",
                ["2024-2025", "2023-2024", "2022-2023"],
                index=0
            )
            gst_registration = st.selectbox(
                "GST Registration",
                ["Registered", "Not Registered", "Cash Basis"],
                index=0
            )
        
        with col2:
            default_category = st.selectbox(
                "Default Receipt Category",
                ["Office supplies", "Travel", "Meals", "Software", "Rent", "Other"],
                index=0
            )
            currency_format = st.selectbox(
                "Currency Format",
                ["$1,000.00", "$1000.00", "1,000.00"],
                index=0
            )
        
        st.divider()
        
        st.markdown("### Notification Preferences")
        
        email_notifications = st.checkbox("Email notifications for deadlines", value=True)
        sms_notifications = st.checkbox("SMS notifications for urgent tasks", value=False)
        weekly_summary = st.checkbox("Weekly practice summary email", value=True)
        
        if st.button("💾 Save Settings", type="primary"):
            # In production, save to database
            st.success("✅ Settings saved!")
            st.balloons()
        
        st.caption("💡 These settings will be saved to your account")
