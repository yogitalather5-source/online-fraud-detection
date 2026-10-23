import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Online Fraud Detection", page_icon="🛡️", layout="centered")

st.title("🛡️ Online Fraud Detection System")
st.caption("Educational demo • Transaction risk screening")

st.info(
    "This starter project uses transparent demo rules, not a trained machine-learning model. "
    "Its score is illustrative and must not be treated as proof of fraud."
)

st.header("Analyze a transaction")
amount = st.number_input("Transaction amount (₹)", min_value=0.0, value=1500.0, step=100.0)
transaction_type = st.selectbox("Transaction type", ["UPI payment", "Online transfer", "Card payment", "Other"])
new_device = st.checkbox("Transaction is from a new or unrecognized device")
unusual_location = st.checkbox("Transaction is from an unusual location")
repeated_attempts = st.checkbox("Several attempts happened in a short time")

if st.button("Analyze transaction", type="primary", use_container_width=True):
    # Clearly labeled illustrative rules for a classroom prototype only.
    score = 5
    reasons = []
    if amount >= 25000:
        score += 25
        reasons.append("High transaction amount compared with this demo's threshold")
    if new_device:
        score += 25
        reasons.append("New or unrecognized device")
    if unusual_location:
        score += 25
        reasons.append("Unusual location")
    if repeated_attempts:
        score += 20
        reasons.append("Repeated attempts in a short time")
    score = min(score, 99)

    st.subheader("Screening result")
    st.metric("Illustrative risk score", f"{score}/100")
    if score >= 60:
        st.error("Higher risk — review this transaction")
    elif score >= 30:
        st.warning("Medium risk — verify the details")
    else:
        st.success("Lower risk based on the selected demo indicators")

    if reasons:
        st.write("**Indicators that contributed to the score:**")
        for reason in reasons:
            st.write(f"- {reason}")
    else:
        st.write("No demo risk indicators were selected.")

    st.caption("This is not a real fraud probability. Real systems need validated data, testing, and human review.")

st.divider()
st.header("Try sample records")
sample = pd.DataFrame([
    {"Transaction ID": "TXN-001", "Amount (₹)": 450, "New device": "No", "Unusual location": "No", "Repeated attempts": "No", "Label": "Demo only"},
    {"Transaction ID": "TXN-002", "Amount (₹)": 42000, "New device": "Yes", "Unusual location": "Yes", "Repeated attempts": "No", "Label": "Demo only"},
    {"Transaction ID": "TXN-003", "Amount (₹)": 2300, "New device": "No", "Unusual location": "Yes", "Repeated attempts": "Yes", "Label": "Demo only"},
])
st.dataframe(sample, use_container_width=True, hide_index=True)

st.subheader("Upload a CSV for a basic preview")
uploaded = st.file_uploader("Choose a CSV file", type=["csv"])
if uploaded:
    try:
        df = pd.read_csv(uploaded)
        st.write("Rows:", len(df), " • Columns:", len(df.columns))
        st.dataframe(df.head(20), use_container_width=True)
        st.caption("The uploaded file is only previewed; no fraud predictions are made on it.")
    except Exception as exc:
        st.error(f"Could not read the CSV: {exc}")

st.divider()
st.caption("Privacy note: Use synthetic or anonymized data. Do not upload card numbers, passwords, OTPs, or real customer financial details.")
