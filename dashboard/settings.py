import streamlit as st
from db import get_db, User

def show_settings(db):
    st.subheader("⚙️ Account Settings")
    
    user_id = st.session_state.user_id
    user = db.query(User).filter(User.id == user_id).first()
    
    if user:
        col1, col2 = st.columns(2)
        with col1:
            firm_name = st.text_input("Firm Name", value=user.firm_name)
            email = st.text_input("Email", value=user.email)
        with col2:
            agent_code = st.text_input("ATO Agent Code", value=user.agent_code or "")
        
        if st.button("Update Profile", type="primary"):
            if firm_name and email:
                user.firm_name = firm_name
                user.email = email
                user.agent_code = agent_code
                db.commit()
                st.success("Profile updated!")
                st.rerun()
