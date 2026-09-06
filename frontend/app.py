import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="AI Contract Analyzer", page_icon="⚖️", layout="wide")
st.title("⚖️ AI Contract Analyzer")
st.caption("100% local — your documents never leave your machine")

# Role selection
st.subheader("1. Who are you in this contract?")
role = st.selectbox(
    "I am the:",
    ["Employee", "Employer", "Tenant", "Landlord",
     "Service Provider", "Client", "Buyer", "Seller", "Other"]
)

# File upload
st.subheader("2. Upload your contract")
uploaded_file = st.file_uploader(
    "Choose a file",
    type=["pdf", "docx", "txt"]
)

if st.button("🔍 Analyze Contract", type="primary") and uploaded_file and role:
    with st.spinner(f"Analyzing from {role} perspective... (may take a minute)"):
        response = requests.post(
            f"{BACKEND_URL}/analyze",
            files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)},
            data={"role": role},
            timeout=1200
        )
        result = response.json()

    if "error" in result:
        st.error(result["error"])
    else:
        # Header metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Contract Type", result.get("contract_type", "Unknown"))
        col2.metric("Overall Risk", result.get("overall_risk", "Unknown"))
        col3.metric("Risk Score", f"{result.get('risk_score', 0)}/100")

        # Summary
        st.subheader("📋 Summary")
        st.write(result.get("summary"))

        # Flagged clauses
        st.subheader("🚨 Flagged Clauses")
        flagged = result.get("flagged_clauses", [])

        if not flagged:
            st.success("No risky clauses found!")
        else:
            for i, clause in enumerate(flagged):
                risk = clause.get("risk_level", "Low")
                color = "🔴" if risk == "High" else "🟡" if risk == "Medium" else "🟢"

                with st.expander(f"{color} Clause {i+1} — {risk} Risk"):
                    st.markdown("**Original Clause:**")
                    st.info(clause.get("clause"))

                    st.markdown("**Why it's risky:**")
                    st.warning(clause.get("reason"))

                    st.markdown("**Suggested Improvement:**")
                    st.success(clause.get("suggestion"))

        # Raw Analysis
        if result.get("raw_analysis"):
            st.subheader("📋 Full Analysis")
            st.markdown(result.get("raw_analysis"))