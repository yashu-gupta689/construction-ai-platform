import os
import pandas as pd
import streamlit as st

# Streamlit Cloud ke Secrets se key lein (local me .env se aayegi)
try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

from epic3_planning_valuation import run_planning_and_valuation

st.set_page_config(page_title="Construction Planning & Valuation", layout="wide")
st.title("🏗️ Construction Planning & Valuation")
st.caption("AI-driven cost estimate, schedule and real estate valuation (Gemini)")

with st.form("params_form"):
    c1, c2, c3 = st.columns(3)
    location = c1.text_input("Location", "Indore, India")
    area = c2.number_input("Built-up area (sqft)", min_value=200, value=2000, step=100)
    floors = c3.number_input("Floors", min_value=1, max_value=10, value=2)

    c4, c5, c6 = st.columns(3)
    quality = c4.selectbox("Quality", ["economy", "standard", "premium"], index=1)
    project_type = c5.selectbox("Project type", ["residential", "commercial"])
    months = c6.number_input("Target duration (months)", min_value=1, max_value=60, value=10)

    submitted = st.form_submit_button("Generate Plan & Valuation")

if submitted:
    params = {
        "location": location,
        "built_up_area_sqft": int(area),
        "floors": int(floors),
        "quality": quality,
        "project_type": project_type,
        "target_months": int(months),
    }
    try:
       with st.spinner("AI analysis in progress. This may take 30 to 60 seconds..."):
            result = run_planning_and_valuation(params)
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

    plan, val = result["plan"], result["valuation"]
    cost = plan["cost_estimate"]

    st.subheader("💰 Cost Estimate")
    m1, m2 = st.columns(2)
    m1.metric("Total cost", f"₹{cost['total_cost']:,.0f}")
    m2.metric("Cost per sqft", f"₹{cost['cost_per_sqft']:,.0f}")
    st.bar_chart(pd.Series(cost["breakdown"]))

    st.subheader("🧱 Materials")
    st.dataframe(pd.DataFrame(plan["materials"]), use_container_width=True)

    st.subheader("📅 Schedule")
    for p in plan["schedule"]:
        with st.expander(f"{p['phase']} ({p['duration_weeks']} weeks)"):
            for t in p["tasks"]:
                st.write("•", t)

    r1, r2 = st.columns(2)
    with r1:
        st.subheader("⚠️ Risks")
        for r in plan["risks"]:
            st.write("•", r)
    with r2:
        st.subheader("📝 Assumptions")
        for a in plan["assumptions"]:
            st.write("•", a)

    st.subheader("🏠 Real Estate Valuation")
    v1, v2, v3, v4 = st.columns(4)
    v1.metric("Market value", f"₹{val['estimated_market_value']:,.0f}")
    v2.metric("Price per sqft", f"₹{val['price_per_sqft']:,.0f}")
    v3.metric("ROI", f"{val['roi_percent']}%")
    v4.metric("Verdict", str(val["investment_verdict"]).title())
    st.write(f"**Range:** ₹{val['value_range']['low']:,.0f} to ₹{val['value_range']['high']:,.0f}")
    st.write("**Key factors:**")
    for k in val["key_factors"]:
        st.write("•", k)
    st.info(val["reasoning"])

    st.caption("These are AI-generated estimates. Please verify with local rates before making real decisions.")