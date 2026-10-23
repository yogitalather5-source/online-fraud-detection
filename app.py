import streamlit as st
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime

st.set_page_config(
    page_title="Online Fraud Detection",
    page_icon="🛡️",
    layout="wide"
)

# Initialize history for the current session
if "history" not in st.session_state:
    st.session_state.history = []

if "transaction_id" not in st.session_state:
    st.session_state.transaction_id = 1

st.title("🛡️ Online Fraud Detection System")
st.caption("Educational demo | Transaction and URL risk screening")

st.info(
    "This is a rule-based educational project, not a trained "
    "machine-learning model. Scores are illustrative, not proof of fraud."
)

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Transaction Checker", "URL Checker", "History"]
)


# Save results to history
def save_result(check_type, item, score, result, reasons):
    st.session_state.history.append({
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Type": check_type,
        "Item": str(item),
        "Risk Score": score,
        "Result": result,
        "Reasons": ", ".join(reasons) if reasons else "No flagged indicators"
    })


# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.header("📊 Dashboard")

    history = st.session_state.history
    df = pd.DataFrame(history)

    total = len(history)
    high = sum(
        1 for x in history
        if x["Risk Score"] >= 60
    )
    medium = sum(
        1 for x in history
        if 30 <= x["Risk Score"] < 60
    )
    low = total - high - medium

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Checks", total)
    c2.metric("Higher Risk", high)
    c3.metric("Medium Risk", medium)
    c4.metric("Lower Risk", low)

    if total:
        st.subheader("Risk Distribution")
        chart_data = pd.DataFrame({
            "Category": ["Higher Risk", "Medium Risk", "Lower Risk"],
            "Count": [high, medium, low]
        }).set_index("Category")
        st.bar_chart(chart_data)

        st.subheader("Recent Activity")
        st.dataframe(
            df.tail(10).iloc[::-1],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No checks yet. Use Transaction Checker or URL Checker.")


# ---------------- TRANSACTION CHECKER ----------------
elif page == "Transaction Checker":
    st.header("💳 Analyze a Transaction")

    amount = st.number_input(
        "Transaction amount (₹)",
        min_value=0.0,
        value=1500.0,
        step=100.0
    )

    transaction_type = st.selectbox(
        "Transaction type",
        ["UPI payment", "Online transfer", "Card payment", "Other"]
    )

    new_device = st.checkbox(
        "Transaction is from a new or unrecognized device"
    )
    unusual_location = st.checkbox(
        "Transaction is from an unusual location"
    )
    repeated_attempts = st.checkbox(
        "Several attempts happened in a short time"
    )

    if st.button("Analyze Transaction", type="primary"):
        score = 5
        reasons = []

        if amount >= 25000:
            score += 25
            reasons.append("High transaction amount")

        if new_device:
            score += 25
            reasons.append("New or unrecognized device")

        if unusual_location:
            score += 25
            reasons.append("Unusual location")

        if repeated_attempts:
            score += 20
            reasons.append("Repeated attempts")

        score = min(score, 99)

        if score >= 60:
            result = "Higher Risk"
        elif score >= 30:
            result = "Medium Risk"
        else:
            result = "Lower Risk"

        save_result(
            "Transaction",
            f"₹{amount:.2f} | {transaction_type}",
            score,
            result,
            reasons
        )

        st.subheader("Screening Result")
        st.metric("Illustrative Risk Score", f"{score}/100")

        if score >= 60:
            st.error("Higher risk — review the transaction.")
        elif score >= 30:
            st.warning("Medium risk — verify the details.")
        else:
            st.success("Lower risk based on selected indicators.")

        st.write("**Risk indicators:**")
        if reasons:
            for reason in reasons:
                st.write(f"- {reason}")
        else:
            st.write("No demo risk indicators were selected.")

        st.caption(
            "This score is not a real fraud probability."
        )


# ---------------- URL CHECKER ----------------
elif page == "URL Checker":
    st.header("🔗 Suspicious URL Checker")
    st.write("Enter a website link to screen it for common warning signs.")

    url = st.text_input(
        "Website URL",
        placeholder="https://example.com"
    )

    if st.button("Check URL", type="primary"):
        score = 0
        reasons = []

        parsed = None
        valid = False

        try:
            parsed = urlparse(url.strip())
            valid = (
                parsed.scheme in ("http", "https")
                and bool(parsed.hostname)
                and not any(c.isspace() for c in url.strip())
                and not any(ord(c) < 32 for c in url.strip())
                and parsed.username is None
                and parsed.password is None
                and parsed.port is not None
                if parsed.port is not None
                else (
                    parsed.scheme in ("http", "https")
                    and bool(parsed.hostname)
                    and not any(c.isspace() for c in url.strip())
                    and not any(ord(c) < 32 for c in url.strip())
                    and parsed.username is None
                    and parsed.password is None
                )
            )
        except ValueError:
            valid = False

        if not url.strip() or not valid:
            st.error(
                "Enter a valid URL starting with http:// or https://."
            )
        else:
            host = parsed.hostname.lower()
            full_url = url.strip().lower()

            if parsed.scheme != "https":
                score += 15
                reasons.append("Website does not use HTTPS")

            if "@" in url.strip():
                score += 25
                reasons.append("URL contains an @ symbol")

            if len(url.strip()) > 100:
                score += 10
                reasons.append("Unusually long URL")

            if host.startswith("xn--") or ".xn--" in host:
                score += 20
                reasons.append("Domain uses encoded characters")

            try:
                import ipaddress
                ipaddress.ip_address(host)
                score += 25
                reasons.append("Website uses an IP address instead of a domain")
            except ValueError:
                pass

            shorteners = [
                "bit.ly", "tinyurl.com", "t.co",
                "is.gd", "cutt.ly", "shorturl.at"
            ]

            if host in shorteners:
                score += 20
                reasons.append("URL uses a shortening service")

            suspicious_words = [
                "verify", "login", "free-prize",
                "claim-reward", "password", "urgent"
            ]

            if any(word in full_url for word in suspicious_words):
                score += 15
                reasons.append("URL contains potentially suspicious words")

            score = min(score, 99)

            if score >= 60:
                result = "Higher Risk"
            elif score >= 30:
                result = "Medium Risk"
            else:
                result = "Lower Risk"

            save_result("URL", url.strip(), score, result, reasons)

            st.subheader("URL Screening Result")
            st.metric("Illustrative Risk Score", f"{score}/100")

            if score >= 60:
                st.error("Higher risk — avoid opening until verified.")
            elif score >= 30:
                st.warning("Medium risk — verify the website carefully.")
            else:
                st.success("Few warning signs detected by these rules.")

            if reasons:
                st.write("**Warning signs:**")
                for reason in reasons:
                    st.write(f"- {reason}")
            else:
                st.write("No warning signs were detected by these rules.")

            st.caption(
                "This checker does not visit the URL or verify its "
                "reputation. A low score does not mean a site is safe."
            )


# ---------------- HISTORY ----------------
elif page == "History":
    st.header("🕒 Check History")

    history = st.session_state.history

    if history:
        df = pd.DataFrame(history)

        search = st.text_input("Search history")
        if search:
            df = df[
                df.astype(str).apply(
                    lambda row: row.str.contains(
                        search, case=False, regex=False
                    ).any(),
                    axis=1
                )
            ]

        st.dataframe(
            df.iloc[::-1],
            use_container_width=True,
            hide_index=True
        )

        csv = pd.DataFrame(history).to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download History as CSV",
            data=csv,
            file_name="fraud_detection_history.csv",
            mime="text/csv"
        )

        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("Your checked transactions and URLs will appear here.")

st.divider()
st.caption(
    "Educational project only. Use synthetic data. "
    "Do not enter passwords, OTPs, card numbers, or personal financial data."
)

     
        
