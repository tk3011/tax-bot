import streamlit as st
import pandas as pd
from datetime import datetime
import io

def show_bas_generator(db, Receipt, Client):
    st.subheader("📋 BAS Statement Generator")
    st.markdown("*Generate Business Activity Statements for GST reporting*")
    
    user_id = st.session_state.user_id
    clients = db.query(Client).filter(Client.user_id == user_id).all()
    
    if not clients:
        st.warning("⚠️ No clients found. Please add clients first in the Clients page.")
        return
    
    selected_client = st.selectbox("Select Client", [c.name for c in clients])
    
    # BAS Period
    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox("BAS Period", ["Monthly", "Quarterly", "Annual"])
    with col2:
        if period == "Monthly":
            month = st.selectbox("Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
            year = st.number_input("Year", min_value=2020, max_value=2030, value=datetime.now().year)
            period_label = f"{month} {year}"
        elif period == "Quarterly":
            quarter = st.selectbox("Quarter", ["Q1 (Jul-Sep)", "Q2 (Oct-Dec)", "Q3 (Jan-Mar)", "Q4 (Apr-Jun)"])
            year = st.number_input("Year", min_value=2020, max_value=2030, value=datetime.now().year)
            period_label = f"{quarter} {year}"
        else:
            year = st.number_input("Financial Year", min_value=2020, max_value=2030, value=datetime.now().year)
            period_label = f"FY {year-1}/{year}"
    
    st.divider()
    
    # GST Calculations
    st.subheader("💰 GST Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Sales (GST on Sales)**")
        gst_sales = st.number_input("Total Sales (Excluding GST)", min_value=0, value=50000, step=5000)
        gst_on_sales = gst_sales * 0.1
        st.metric("GST on Sales", f"${gst_on_sales:,.2f}")
    
    with col2:
        st.markdown("**Purchases (GST on Purchases)**")
        gst_purchases = st.number_input("Total Purchases (Excluding GST)", min_value=0, value=25000, step=5000)
        gst_on_purchases = gst_purchases * 0.1
        st.metric("GST on Purchases", f"${gst_on_purchases:,.2f}")
    
    st.divider()
    
    # Calculate BAS
    net_gst = gst_on_sales - gst_on_purchases
    
    st.subheader("📊 BAS Calculation")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("GST on Sales", f"${gst_on_sales:,.2f}")
    with col2:
        st.metric("GST on Purchases", f"${gst_on_purchases:,.2f}")
    with col3:
        if net_gst > 0:
            st.metric("Net GST Payable", f"${net_gst:,.2f}", delta="To ATO", delta_color="inverse")
        else:
            st.metric("Net GST Refund", f"${abs(net_gst):,.2f}", delta="From ATO")
    
    # PAYG Withholding
    st.subheader("🏦 PAYG Withholding")
    payg_withholding = st.number_input("PAYG Withholding (Total wages paid)", min_value=0, value=5000, step=1000)
    
    # BAS Summary
    st.divider()
    st.subheader("📄 BAS Summary")
    
    bas_data = {
        "Label": [
            "G1 - Total sales (GST inclusive)",
            "G2 - Export sales",
            "G3 - Other GST-free sales",
            "1A - GST on sales",
            "1B - GST on purchases",
            "4 - PAYG withholding",
            "5A - Total GST payable/refund"
        ],
        "Amount": [
            f"${gst_sales + gst_on_sales:,.2f}",
            "$0.00",
            "$0.00",
            f"${gst_on_sales:,.2f}",
            f"${gst_on_purchases:,.2f}",
            f"${payg_withholding:,.2f}",
            f"${net_gst:,.2f}"
        ]
    }
    
    bas_df = pd.DataFrame(bas_data)
    st.dataframe(bas_df, use_container_width=True, hide_index=True)
    
    # Generate BAS File
    total_payment = net_gst + payg_withholding if net_gst > 0 else payg_withholding
    
    st.info(f"**Total Amount {'Payable' if net_gst > 0 else 'Refundable'}:** ${abs(total_payment):,.2f}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Generate BAS Statement", type="primary", use_container_width=True):
            bas_file = f"""ATO BAS Statement
Generated: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Firm: {st.session_state.firm_name}

BAS DETAILS
Client: {selected_client}
Period: {period_label}

BAS CALCULATION
G1 - Total sales (incl GST): ${gst_sales + gst_on_sales:,.2f}
1A - GST on sales: ${gst_on_sales:,.2f}
1B - GST on purchases: ${gst_on_purchases:,.2f}
4 - PAYG Withholding: ${payg_withholding:,.2f}
5A - Net GST: ${net_gst:,.2f}

PAYMENT DETAILS
Total {'Payable' if net_gst > 0 else 'Refundable'}: ${abs(total_payment):,.2f}
Due Date: 28th of next month

LODGMENT INSTRUCTIONS
1. Review all figures
2. Lodge via ATO Business Portal
3. Keep this record for your files
"""
            st.success("✅ BAS Statement Generated!")
            st.download_button(
                label="📥 Download BAS Statement",
                data=bas_file,
                file_name=f"BAS_{selected_client.replace(' ', '_')}_{period_label.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
            st.balloons()
    
    with col2:
        st.caption("💡 Tip: You can lodge BAS directly through the ATO Business Portal")
