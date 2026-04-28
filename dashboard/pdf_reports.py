import streamlit as st
from datetime import datetime

def show_pdf_reports(db, Receipt, Client):
    st.subheader("📄 PDF Tax Reports")
    st.markdown("*Generate professional PDF summaries of tax returns*")
    
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
    
    # Show client details
    if selected_client:
        st.info(f"**Client:** {selected_client.name} | **TFN:** {selected_client.tfn or 'Not provided'}")
    
    st.divider()
    
    # Income Section
    st.subheader("💰 Income")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        employment_income = st.number_input("Employment Income", min_value=0, value=75000, step=5000)
    with col2:
        business_income = st.number_input("Business Income", min_value=0, value=0, step=1000)
    with col3:
        investment_income = st.number_input("Investment Income", min_value=0, value=0, step=1000)
    
    total_income = employment_income + business_income + investment_income
    st.metric("Total Income", f"${total_income:,.2f}")
    
    # Deductions
    st.subheader("📉 Deductions")
    
    if receipts:
        deductions_by_category = {}
        for r in receipts:
            deductions_by_category[r.category] = deductions_by_category.get(r.category, 0) + r.amount
        
        for cat, amt in deductions_by_category.items():
            st.write(f"**{cat}:** ${amt:,.2f}")
        
        total_deductions = sum(r.amount for r in receipts)
        st.caption(f"📸 From {len(receipts)} scanned receipts")
    else:
        total_deductions = 0
        st.info("No receipts added yet. Use Receipt Scanner to add deductions.")
    
    # Tax Withholding
    st.subheader("🏦 Tax Already Paid")
    tax_withheld = st.number_input("PAYG Withholding", min_value=0, value=15000, step=1000)
    
    # Calculate tax
    taxable_income = max(0, total_income - total_deductions)
    
    if taxable_income <= 18200:
        income_tax = 0
    elif taxable_income <= 45000:
        income_tax = (taxable_income - 18200) * 0.16
    elif taxable_income <= 135000:
        income_tax = 4288 + (taxable_income - 45000) * 0.30
    elif taxable_income <= 190000:
        income_tax = 31288 + (taxable_income - 135000) * 0.37
    else:
        income_tax = 51488 + (taxable_income - 190000) * 0.45
    
    medicare = taxable_income * 0.02 if taxable_income > 32000 else 0
    total_tax = income_tax + medicare
    refund = tax_withheld - total_tax
    
    # Show calculation
    st.divider()
    st.subheader("🧮 Tax Calculation")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Income Tax: ${income_tax:,.2f}")
        st.write(f"Medicare Levy: ${medicare:,.2f}")
        st.write(f"**Total Tax Liability:** ${total_tax:,.2f}")
    
    with col2:
        if refund > 0:
            st.metric("Estimated Refund", f"${refund:,.2f}", delta="Refund")
        elif refund < 0:
            st.metric("Amount Owing", f"${abs(refund):,.2f}", delta="To pay")
        else:
            st.metric("Break Even", "$0")
    
    # Generate PDF Button
    if st.button("📄 Generate PDF Report", type="primary", use_container_width=True):
        with st.spinner("Generating PDF..."):
            # Create text report (in production, use reportlab for real PDFs)
            report = f"""TAX RETURN REPORT - {financial_year}
Generated: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Prepared by: {st.session_state.firm_name}

CLIENT INFORMATION
Name: {selected_client.name}
Email: {selected_client.email}
TFN: {selected_client.tfn or 'Not provided'}
Phone: {selected_client.phone or 'Not provided'}

INCOME SUMMARY
Employment Income: ${employment_income:,.2f}
Business Income: ${business_income:,.2f}
Investment Income: ${investment_income:,.2f}
TOTAL INCOME: ${total_income:,.2f}

DEDUCTION SUMMARY
"""
            if receipts:
                for cat, amt in deductions_by_category.items():
                    report += f"{cat}: ${amt:,.2f}\n"
                report += f"TOTAL DEDUCTIONS: ${total_deductions:,.2f}\n"
            else:
                report += "No deductions recorded\n"
            
            report += f"""
TAX CALCULATION
Taxable Income: ${taxable_income:,.2f}
Income Tax Payable: ${income_tax:,.2f}
Medicare Levy: ${medicare:,.2f}
TOTAL TAX LIABILITY: ${total_tax:,.2f}
PAYG Withheld: ${tax_withheld:,.2f}

RESULT
{'REFUND DUE: $' + f'{refund:,.2f}' if refund > 0 else 'AMOUNT OWING: $' + f'{abs(refund):,.2f}' if refund < 0 else 'NIL'}

REPORT GENERATED BY TAX BOT
This is an AI-generated summary. Please review before lodgment.
"""
            
            st.success("✅ PDF Report Generated!")
            st.download_button(
                label="📥 Download Report",
                data=report,
                file_name=f"tax_report_{selected_client.name.replace(' ', '_')}_{financial_year}.txt",
                mime="text/plain"
            )
            st.balloons()
    
    st.caption("💡 Professional PDF reports with full formatting will be available in the next update")
