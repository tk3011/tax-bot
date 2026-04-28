import streamlit as st
import time
from datetime import datetime

def show_portal_jockey(db, Receipt, Client):
    st.subheader("🔐 ATO Portal Integration")
    st.markdown("*Connect to ATO systems for pre-filled data and lodgment*")
    
    user_id = st.session_state.user_id
    clients = db.query(Client).filter(Client.user_id == user_id).all()
    
    st.info("""
    **ATO Digital Service Provider (DSP) Integration**
    
    Your bot is ready to connect to ATO systems. To enable full integration:
    
    1. Register as a DSP with the ATO
    2. Complete the security questionnaire
    3. Get your M2M credentials
    4. Configure TLS 1.3
    
    **Current Status:** Demo Mode - Simulating ATO data
    """)
    
    if not clients:
        st.warning("No clients found. Add clients first to test ATO data fetching.")
        return
    
    tab1, tab2, tab3 = st.tabs(["📥 Pre-fill Data", "📄 ATO Documents", "🔗 Client Linking"])
    
    with tab1:
        st.markdown("### Fetch Pre-fill Reports")
        
        selected_clients = st.multiselect("Select clients", [c.name for c in clients])
        
        fetch_type = st.radio(
            "Data to fetch",
            ["Income Statements", "Bank Interest", "Dividends", "All Pre-fill Data"],
            horizontal=True
        )
        
        if st.button("🚀 Fetch from ATO", type="primary"):
            if not selected_clients:
                st.error("Select at least one client")
            else:
                progress = st.progress(0)
                results = []
                
                for i, client in enumerate(selected_clients):
                    time.sleep(0.5)
                    progress.progress((i + 1) / len(selected_clients))
                    results.append({
                        "Client": client,
                        "Status": "Success",
                        "Data": f"{fetch_type} retrieved",
                        "Time": datetime.now().strftime("%H:%M:%S")
                    })
                
                progress.empty()
                
                import pandas as pd
                st.success(f"✅ Retrieved data for {len(results)} clients")
                st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
                
                for client in selected_clients:
                    st.download_button(
                        label=f"📥 Download {client} - {fetch_type}",
                        data=f"Sample {fetch_type} data for {client}\n\nThis is demo data. Real ATO integration requires DSP registration.",
                        file_name=f"prefill_{client.replace(' ', '_')}.csv",
                        key=f"download_{client}"
                    )
                
                st.balloons()
    
    with tab2:
        st.markdown("### ATO Document Management")
        
        doc_types = st.multiselect(
            "Document types",
            ["Notice of Assessment", "Payment Summary", "Activity Statement", "Tax Return Copy"]
        )
        
        if st.button("📄 Retrieve Documents"):
            if not doc_types:
                st.error("Select document types")
            else:
                with st.spinner("Connecting to ATO..."):
                    time.sleep(1.5)
                st.success(f"Retrieved {len(doc_types)} document types")
                
                for doc in doc_types:
                    with st.expander(f"📁 {doc}"):
                        st.write(f"Available for {len(clients)} clients")
                        if st.button(f"Download {doc}", key=f"doc_{doc}"):
                            st.info(f"Demo: {doc} would be downloaded here")
    
    with tab3:
        st.markdown("### Client-Agent Linking (CAL)")
        st.info("🔗 The linking process normally takes 5-7 days manually. Automation reduces it to minutes.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            client_name = st.text_input("Client Full Name")
            client_email = st.text_input("Client Email")
        
        with col2:
            client_tfn = st.text_input("Client TFN")
            auth_method = st.selectbox("Authorization Method", ["Email Invitation", "SMS Code"])
        
        if st.button("🔗 Send Linking Request", type="primary"):
            if client_name and client_email:
                with st.spinner(f"Sending linking request to {client_email}..."):
                    time.sleep(1.5)
                st.success(f"✅ Linking request sent to {client_email}")
                st.info("Client will receive an email to authorize you as their tax agent")
                st.balloons()
            else:
                st.error("Please enter client name and email")
    
    # DSP Registration Info
    with st.expander("📖 How to Get Real ATO Access (DSP Registration)"):
        st.markdown("""
        **Steps to register as a Digital Service Provider:**
        
        1. **Register for API Portal account** at apiportal.ato.gov.au
        2. **Create a Team** (your business/company)
        3. **Complete security questionnaire** (1-2 weeks)
        4. **Subscribe to required APIs** (PLS, CAL, etc.)
        5. **Get M2M credentials** via Relationship Authorisation Manager
        6. **Implement TLS 1.3** (required by Jan 2026)
        7. **Notify Software ID** to ATO by June 2026
        
        **Once registered, your bot can:**
        - Automatically download pre-fill reports for any authorized client
        - Lodge tax returns directly via PLS
        - Automated client-agent linking (reducing 5-7 days to minutes)
        - Real-time ATO data synchronization
        
        **Demo mode is active now** - showing what's possible with full integration.
        """)
