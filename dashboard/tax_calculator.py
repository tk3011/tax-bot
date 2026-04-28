import streamlit as st
from datetime import datetime

def show_tax_return(db, Receipt, Client):
    st.subheader("📄 Tax Return Preparation")
    st.markdown("*Calculate tax liability and prepare lodgment*")
    
    user_id = st.session_state.user_id
    clients = db.query(Client).filter(Client.user_id == user_id).all()
    receipts = db.query(Receipt).filter(Receipt.user_id == user_id).all()
    
    if not clients:
        st.warning("⚠️ No clients found. Please add clients first in the Clients page.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_client_name = st.selectbox("Select Client", [c.name for c in clients])
        selected_client = next((c for c in clients if c.name == selected_client_name), None)
    
    with col2:
        financial_year = st.selectbox("Financial Year", ["2024-2025", "2023-2024", "2022-2023"])
    
    if selected_client:
        st.success(f"Preparing {financial_year} tax return for {selected_client_name}")
        if selected_client.tfn:
            st.caption(f"TFN: {selected_client.tfn}")
    
    st.divider()
    
    # Income Section
    st.subheader("💰 Income")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        employment_income = st.number_input("Employment Income", min_value=0, value=75000, step=5000)
    with col2:
        business_income = st.number_input("Business Income", min_value=0, value=0, step=1000)
    with col3:
        other_income = st.number_input("Other Income", min_value=0, value=0, step=1000)
    
    total_income = employment_income + business_income + other_income
    st.metric("Total Income", f"${total_income:,.2f}")
    
    # Deductions Section
    st.subheader("📉 Deductions")
    
    total_deductions = 0
    
    if receipts:
        deductions_by_category = {}
        for r in receipts:
            deductions_by_category[r.category] = deductions_by_category.get(r.category, 0) + r.amount
        
        st.markdown("**From Scanned Receipts:**")
        for cat, amt in deductions_by_category.items():
            st.write(f"• {cat}: ${amt:,.2f}")
        
        total_deductions = sum(r.amount for r in receipts)
        st.caption(f"📸 Total from {len(receipts)} receipts: ${total_deductions:,.2f}")
    else:
        st.info("No receipts added yet. Use Receipt Scanner to add deductions.")
    
    # Manual deductions
    with st.expander("➕ Add Manual Deductions"):
        col1, col2 = st.columns(2)
        with col1:
            car_expenses = st.number_input("Car Expenses", min_value=0, value=0, step=100)
            travel = st.number_input("Travel Expenses", min_value=0, value=0, step=100)
        with col2:
            education = st.number_input("Education Expenses", min_value=0, value=0, step=100)
            manual_other = st.number_input("Other Deductions", min_value=0, value=0, step=100)
        
        manual_deductions = car_expenses + travel + education + manual_other
        if manual_deductions > 0:
            st.write(f"Manual deductions total: ${manual_deductions:,.2f}")
            total_deductions = total_deductions + manual_deductions
    
    st.metric("Total Deductions", f"${total_deductions:,.2f}")
    
    # Tax Withholding
    st.subheader("🏦 Tax Already Paid")
    tax_withheld = st.number_input("PAYG Withholding (from payment summary)", min_value=0, value=15000, step=1000)
    
    # Tax Calculation
    st.divider()
    st.subheader("🧮 Tax Calculation")
    
    taxable_income = max(0, total_income - total_deductions)
    st.metric("Taxable Income", f"${taxable_income:,.2f}", delta=f"minus ${total_deductions:,.2f} deductions")
    
    # Australian tax brackets 2024-2025
    if taxable_income <= 18200:
        income_tax = 0
        bracket = "Tax-free threshold"
    elif taxable_income <= 45000:
        income_tax = (taxable_income - 18200) * 0.16
        bracket = "16% bracket"
    elif taxable_income <= 135000:
        income_tax = 4288 + (taxable_income - 45000) * 0.30
        bracket = "30% bracket"
    elif taxable_income <= 190000:
        income_tax = 31288 + (taxable_income - 135000) * 0.37
        bracket = "37% bracket"
    else:
        income_tax = 51488 + (taxable_income - 190000) * 0.45
        bracket = "45% bracket"
    
    # Medicare Levy
    if taxable_income <= 32000:
        medicare = 0
        medicare_note = "Below threshold"
    elif taxable_income <= 39000:
        medicare = taxable_income * 0.02 * 0.5
        medicare_note = "Reduced rate"
    else:
        medicare = taxable_income * 0.02
        medicare_note = "Standard rate"
    
    total_tax_liability = income_tax + medicare
    refund_amount = tax_withheld - total_tax_liability
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Tax Breakdown**")
        st.write(f"Income Tax: ${income_tax:,.2f} ({bracket})")
        st.write(f"Medicare Levy: ${medicare:,.2f} ({medicare_note})")
        st.write(f"**Total Liability:** ${total_tax_liability:,.2f}")
    
    with col2:
        st.markdown("**Result**")
        if refund_amount > 0:
            st.metric("Estimated Refund", f"${refund_amount:,.2f}", delta="You get this back")
            st.success(f"🎉 Based on your data, you may receive a refund of ${refund_amount:,.2f}")
        elif refund_amount < 0:
            st.metric("Amount Owing", f"${abs(refund_amount):,.2f}", delta="To pay to ATO")
            st.warning(f"⚠️ Based on your data, you may owe ${abs(refund_amount):,.2f} to the ATO")
        else:
            st.metric("Break Even", "$0")
            st.info("Your tax withheld matches your liability")
    
    # Generate Return Button
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Generate Tax Return", type="primary", use_container_width=True):
            st.session_state['return_generated'] = True
            st.success("Tax return calculated! Ready for review.")
            
            summary = {
                "Client": selected_client_name,
                "Financial Year": financial_year,
                "Taxable Income": f"${taxable_income:,.2f}",
                "Total Deductions": f"${total_deductions:,.2f}",
                "Tax Withheld": f"${tax_withheld:,.2f}",
                "Tax Liability": f"${total_tax_liability:,.2f}",
                "Result": f"${abs(refund_amount):,.2f} {'Refund' if refund_amount > 0 else 'Owing' if refund_amount < 0 else 'Nil'}"
            }
            st.json(summary)
            
            st.download_button(
                label="📥 Download Tax Return Summary",
                data=str(summary),
                file_name=f"tax_return_{selected_client_name.replace(' ', '_')}_{financial_year}.txt",
                key="download_return"
            )
            st.balloons()
    
    with col2:
        st.caption("💡 Review all figures before lodgment")
