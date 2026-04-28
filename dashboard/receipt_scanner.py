import streamlit as st
from datetime import datetime

def show_receipt_scanner(db, Receipt):
    st.subheader("📸 Receipt Entry")
    st.markdown("*Add receipt details manually*")
    
    user_id = st.session_state.user_id
    
    st.subheader("Manual Entry")
    
    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("Amount ($)", min_value=0.0, step=1.0, format="%.2f")
        vendor = st.text_input("Vendor/Store name")
    with col2:
        date = st.date_input("Date", datetime.now())
        category = st.selectbox("Category", ["Office supplies", "Travel", "Meals", "Software", "Rent", "Other"])
    
    if st.button("💾 Save Receipt", type="primary"):
        if amount > 0 and vendor:
            new_receipt = Receipt(
                user_id=user_id,
                amount=amount,
                vendor=vendor,
                date=date.strftime("%Y-%m-%d"),
                category=category
            )
            db.add(new_receipt)
            db.commit()
            st.success(f"✅ Saved ${amount:.2f} from {vendor}")
            st.balloons()
            st.rerun()
        else:
            st.error("Please enter amount and vendor")
    
    st.divider()
    st.subheader("📋 Recent Receipts")
    receipts = db.query(Receipt).filter(Receipt.user_id == user_id).order_by(Receipt.created_at.desc()).limit(10).all()
    if receipts:
        for r in receipts:
            st.write(f"💰 ${r.amount:.2f} - {r.vendor} - {r.date}")
    else:
        st.info("No receipts yet")
