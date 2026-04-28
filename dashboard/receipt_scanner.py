import streamlit as st
from PIL import Image
import re
from datetime import datetime

def show_receipt_scanner(db, Receipt):
    st.subheader("📸 Smart Receipt Scanner")
    st.markdown("*Upload a receipt photo - Enter details manually or use OCR*")
    
    user_id = st.session_state.user_id
    
    # Try to import pytesseract, but don't fail if not available
    try:
        import pytesseract
        OCR_AVAILABLE = True
    except ImportError:
        OCR_AVAILABLE = False
        st.info("🔧 OCR is available in the full version. You can still add receipts manually.")
    
    tab1, tab2 = st.tabs(["✏️ Manual Entry", "📷 Scan Receipt (OCR)" if OCR_AVAILABLE else "📷 Scan Receipt (Coming Soon)"])
    
    with tab1:
        st.subheader("Manual Entry")
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input("Amount ($)", min_value=0.0, step=1.0, key="m_amt")
            vendor = st.text_input("Vendor", key="m_ven")
        with col2:
            date = st.date_input("Date", datetime.now(), key="m_dt")
            category = st.selectbox("Category", ["Office supplies", "Travel", "Meals", "Software", "Rent", "Other"], key="m_cat")
        
        if st.button("Save", key="m_save"):
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
                st.success("Saved!")
                st.rerun()
            else:
                st.error("Enter amount and vendor")
    
    if OCR_AVAILABLE:
        with tab2:
            st.subheader("Scan Receipt with OCR")
            uploaded_file = st.file_uploader("Take a photo or upload a receipt", type=["jpg", "jpeg", "png"], key="scan")
            
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Your receipt", width=300)
                
                with st.spinner("🔍 Reading text from image..."):
                    try:
                        if image.mode in ('RGBA', 'LA', 'P'):
                            image = image.convert('RGB')
                        
                        text = pytesseract.image_to_string(image)
                        
                        amount = None
                        vendor = ""
                        
                        amounts = re.findall(r'\$?\s*(\d+\.\d{2})', text)
                        if amounts:
                            amount = max(float(a) for a in amounts)
                        
                        lines = text.split('\n')
                        for line in lines[:10]:
                            line = line.strip()
                            if 3 < len(line) < 35 and not any(c.isdigit() for c in line[:3]):
                                exclude = ['THANK', 'PLEASE', 'VISIT', 'WEB', 'HTTP', 'WWW', '.COM', '.AU']
                                if not any(w in line.upper() for w in exclude):
                                    vendor = line
                                    break
                        
                        if amount:
                            st.success(f"✅ Detected: ${amount:.2f}")
                        else:
                            st.warning("Could not detect amount")
                        
                    except Exception as e:
                        st.error(f"OCR error: {str(e)}")
                        amount = None
                        vendor = ""
                
                col1, col2 = st.columns(2)
                with col1:
                    amount_input = st.number_input("Amount ($)", value=float(amount) if amount else 0.0, min_value=0.0, step=1.0, key="amt")
                    date_input = st.date_input("Date", datetime.now(), key="dt")
                with col2:
                    vendor_input = st.text_input("Vendor", value=vendor, key="ven")
                    category_input = st.selectbox("Category", ["Office supplies", "Travel", "Meals", "Software", "Rent", "Other"], key="cat")
                
                if st.button("💾 Save Receipt", key="save_ocr", type="primary"):
                    if amount_input > 0 and vendor_input:
                        new_receipt = Receipt(
                            user_id=user_id,
                            amount=amount_input,
                            vendor=vendor_input,
                            date=date_input.strftime("%Y-%m-%d"),
                            category=category_input
                        )
                        db.add(new_receipt)
                        db.commit()
                        st.success(f"✅ Saved ${amount_input:.2f} from {vendor_input}")
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
