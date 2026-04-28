import streamlit as st
from db import get_db, User
import re

def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'firm_name' not in st.session_state:
        st.session_state.firm_name = None

def show_login():
    """Display login page"""
    st.subheader("🔐 Login to Tax Bot")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
            
            if submitted:
                if not email or not password:
                    st.error("Please enter email and password")
                else:
                    db = get_db()
                    user = db.query(User).filter(User.email == email).first()
                    
                    if user and user.check_password(password):
                        st.session_state.logged_in = True
                        st.session_state.user_id = user.id
                        st.session_state.user_email = user.email
                        st.session_state.firm_name = user.firm_name
                        st.success(f"Welcome back, {user.firm_name}!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
                    db.close()
        
        st.divider()
        st.caption("Don't have an account?")
        if st.button("Register New Account", use_container_width=True):
            st.session_state.show_register = True
            st.rerun()

def show_register():
    """Display registration page"""
    st.subheader("📝 Register New Account")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("register_form"):
            firm_name = st.text_input("Firm/Business Name*")
            email = st.text_input("Email*")
            agent_code = st.text_input("ATO Agent Code (if registered)")
            password = st.text_input("Password*", type="password")
            confirm_password = st.text_input("Confirm Password*", type="password")
            
            submitted = st.form_submit_button("Register", type="primary", use_container_width=True)
            
            if submitted:
                errors = []
                if not firm_name:
                    errors.append("Firm name required")
                if not email:
                    errors.append("Email required")
                if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                    errors.append("Invalid email format")
                if not password:
                    errors.append("Password required")
                if password != confirm_password:
                    errors.append("Passwords do not match")
                if len(password) < 6:
                    errors.append("Password must be at least 6 characters")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    db = get_db()
                    existing = db.query(User).filter(User.email == email).first()
                    if existing:
                        st.error("Email already registered")
                    else:
                        new_user = User(
                            email=email,
                            firm_name=firm_name,
                            agent_code=agent_code
                        )
                        new_user.set_password(password)
                        db.add(new_user)
                        db.commit()
                        st.success("✅ Account created! Please login.")
                        st.session_state.show_register = False
                        st.rerun()
                    db.close()
        
        if st.button("← Back to Login", use_container_width=True):
            st.session_state.show_register = False
            st.rerun()

def show_logout():
    """Display logout button in sidebar"""
    st.sidebar.divider()
    st.sidebar.markdown(f"**Logged in as:** {st.session_state.firm_name}")
    st.sidebar.markdown(f"📧 {st.session_state.user_email}")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_email = None
        st.session_state.firm_name = None
        st.session_state.show_register = False
        st.rerun()

def require_auth():
    """Check if user is authenticated, show login if not"""
    init_session_state()
    
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False
    
    if not st.session_state.logged_in:
        if st.session_state.show_register:
            show_register()
        else:
            show_login()
        return False
    
    # Show logout in sidebar
    show_logout()
    return True
