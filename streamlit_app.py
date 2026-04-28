import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Tax Bot", page_icon="🤖", layout="wide")

# Initialize database
def init_db():
    conn = sqlite3.connect('tax_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT, firm_name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS receipts
                 (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, vendor TEXT, date TEXT, category TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS clients
                 (id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT, email TEXT, tfn TEXT, created_at TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Authentication functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_user(email, password):
    conn = sqlite3.connect('tax_bot.db')
    c = conn.cursor()
    c.execute("SELECT id, email, firm_name FROM users WHERE email=? AND password=?", (email, hash_password(password)))
    user = c.fetchone()
    conn.close()
    if user:
        st.session_state.logged_in = True
        st.session_state.user_id = user[0]
        st.session_state.user_email = user[1]
        st.session_state.firm_name = user[2]
        return True
    return False

def register_user(email, password, firm_name):
    conn = sqlite3.connect('tax_bot.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (email, password, firm_name) VALUES (?, ?, ?)", 
                 (email, hash_password(password), firm_name))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

# Initialize session
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Login/Register UI
if not st.session_state.logged_in:
    st.title("🤖 Tax Bot")
    st.markdown("*Automated tax preparation for Australian tax agents*")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login", type="primary"):
            if login_user(email, password):
                st.success(f"Welcome back, {st.session_state.firm_name}!")
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    with tab2:
        firm_name = st.text_input("Firm Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")
        if st.button("Register", type="primary"):
            if password == confirm and len(password) >= 4:
                if register_user(email, password, firm_name):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Email already exists")
            else:
                st.error("Passwords must match and be at least 4 characters")
    st.stop()

# Main App
st.title("🤖 Tax Bot")
st.markdown(f"*Welcome back, {st.session_state.firm_name}!*")

menu = st.sidebar.radio("Menu", ["Dashboard", "Add Receipt", "Clients", "Tax Return", "Export"])

conn = sqlite3.connect('tax_bot.db')
c = conn.cursor()

if menu == "Dashboard":
    st.subheader("📊 Dashboard")
    
    c.execute("SELECT COUNT(*) FROM receipts WHERE user_id=?", (st.session_state.user_id,))
    receipt_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM clients WHERE user_id=?", (st.session_state.user_id,))
    client_count = c.fetchone()[0]
    
    c.execute("SELECT SUM(amount) FROM receipts WHERE user_id=?", (st.session_state.user_id,))
    total = c.fetchone()[0] or 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Receipts", receipt_count)
    col2.metric("Clients", client_count)
    col3.metric("Total Deductions", f"${total:,.2f}")
    
    st.subheader("Recent Receipts")
    c.execute("SELECT amount, vendor, date, category FROM receipts WHERE user_id=? ORDER BY id DESC LIMIT 5", (st.session_state.user_id,))
    for row in c.fetchall():
        st.write(f"💰 ${row[0]:.2f} - {row[1]} - {row[2]} ({row[3]})")

elif menu == "Add Receipt":
    st.subheader("Add Receipt")
    
    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("Amount ($)", min_value=0.0, step=1.0, format="%.2f")
        vendor = st.text_input("Vendor")
    with col2:
        date = st.date_input("Date", datetime.now())
        category = st.selectbox("Category", ["Office supplies", "Travel", "Meals", "Software", "Rent", "Other"])
    
    if st.button("Save Receipt", type="primary"):
        if amount > 0 and vendor:
            c.execute("INSERT INTO receipts (user_id, amount, vendor, date, category, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                     (st.session_state.user_id, amount, vendor, date.strftime("%Y-%m-%d"), category, datetime.now().isoformat()))
            conn.commit()
            st.success(f"Saved ${amount:.2f} from {vendor}")
            st.rerun()

elif menu == "Clients":
    st.subheader("Clients")
    
    tab1, tab2 = st.tabs(["Add Client", "View Clients"])
    
    with tab1:
        name = st.text_input("Client Name")
        email = st.text_input("Email")
        tfn = st.text_input("TFN (optional)")
        if st.button("Save Client"):
            if name and email:
                c.execute("INSERT INTO clients (user_id, name, email, tfn, created_at) VALUES (?, ?, ?, ?, ?)",
                         (st.session_state.user_id, name, email, tfn, datetime.now().isoformat()))
                conn.commit()
                st.success(f"Client {name} added!")
                st.rerun()
    
    with tab2:
        c.execute("SELECT name, email, tfn, created_at FROM clients WHERE user_id=? ORDER BY id DESC", (st.session_state.user_id,))
        for row in c.fetchall():
            with st.expander(f"👤 {row[0]}"):
                st.write(f"Email: {row[1]}")
                st.write(f"TFN: {row[2] or 'Not provided'}")
                st.write(f"Added: {row[3][:10]}")

elif menu == "Tax Return":
    st.subheader("Tax Return")
    
    c.execute("SELECT amount, category FROM receipts WHERE user_id=?", (st.session_state.user_id,))
    receipts = c.fetchall()
    
    if receipts:
        categories = {}
        for amount, category in receipts:
            categories[category] = categories.get(category, 0) + amount
        
        st.subheader("Deductions by Category")
        for cat, amt in categories.items():
            st.write(f"{cat}: ${amt:.2f}")
        
        total = sum(amount for amount, _ in receipts)
        st.subheader(f"Total Deductions: ${total:.2f}")
        
        income = st.number_input("Total Income", value=75000)
        taxable = max(0, income - total)
        st.metric("Taxable Income", f"${taxable:,.2f}")
        
        # Simple tax calculation
        if taxable <= 18200:
            tax = 0
        elif taxable <= 45000:
            tax = (taxable - 18200) * 0.16
        elif taxable <= 135000:
            tax = 4288 + (taxable - 45000) * 0.30
        else:
            tax = 31288 + (taxable - 135000) * 0.37
        
        st.metric("Estimated Tax", f"${tax:,.2f}")
    else:
        st.info("Add receipts first")

elif menu == "Export":
    st.subheader("Export Data")
    
    c.execute("SELECT date, vendor, amount, category FROM receipts WHERE user_id=?", (st.session_state.user_id,))
    data = c.fetchall()
    
    if data:
        df = pd.DataFrame(data, columns=["Date", "Vendor", "Amount", "Category"])
        st.dataframe(df)
        
        csv = df.to_csv(index=False)
        st.download_button("Download CSV", csv, "tax_data.csv", "text/csv")
    else:
        st.info("No data to export")

conn.close()

# Logout button
if st.sidebar.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
