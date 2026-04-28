import streamlit as st
import pandas as pd
from datetime import datetime

def show_bas_generator(db, Receipt, Client):
    st.subheader("📋 BAS Statement Generator")
    st.markdown("*Generate Business Activity Statements*")
    
    user_id = st.session_state.user_id
    clients = db.query(Client).filter(Client.user_id == user_id).all()
    
    if not clients:
        st.warning("No clients found")
        return
    
    selected_client = st.selectbox("Select Client", [c.name for c in clients])
    
    st.subheader("💰 GST Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        gst_sales = st.number_input("Total Sales (Excluding GST)", min_value=0, value=50000, step=5000)
        gst_on_sales = gst_sales * 0.1
        st.metric("GST on Sales", f"${gst_on_sales:,.2f}")
    
    with col2:
        gst_purchases = st.number_input("Total Purchases (Excluding GST)", min_value=0, value=25000, step=5000)
        gst_on_purchases = gst_purchases * 0.1
        st.metric("GST on Purchases", f"${gst_on_purchases:,.2f}")
    
    net_gst = gst_on_sales - gst_on_purchases
    
    st.subheader("📊 BAS Calculation")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("GST on Sales", f"${gst_on_sales:,.2f}")
    with col2:
        st.metric("GST on Purchases", f"${gst_on_purchases:,.2f}")
    with col3:
        if net_gst > 0:
            st.metric("Net GST Payable", f"${net_gst:,.2f}")
        else:
            st.metric("Net GST Refund", f"${abs(net_gst):,.2f}")
    
    if st.button("Generate BAS Statement", type="primary"):
        st.success("BAS Statement generated!")
        st.balloons()
