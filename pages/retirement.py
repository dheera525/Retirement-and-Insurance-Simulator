import streamlit as st
import pandas as pd
import altair as alt

# ============================================================
# UI SCALE
# ============================================================
st.markdown("""
<style>
html, body, [class*="css"] { font-size: 17px; }
h1 { font-size: 2.4rem; }
h2 { font-size: 1.9rem; }
h3 { font-size: 1.5rem; }
.small-note {
    font-size: 13px;
    color: #9ca3af;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONSTANTS
# ============================================================
INFLATION = 0.06
POST_RET_RETURN = 0.05
MAX_SIP_GROWTH = 0.15

ASSET_RETURNS = {
    "Equity": 0.12,
    "Debt": 0.07,
    "Gold": 0.06,
    "Savings": 0.04
}

RISK_ALLOC = {
    1: {"Equity": 0.25, "Debt": 0.45, "Gold": 0.10, "Savings": 0.20},
    2: {"Equity": 0.35, "Debt": 0.40, "Gold": 0.10, "Savings": 0.15},
    3: {"Equity": 0.50, "Debt": 0.30, "Gold": 0.10, "Savings": 0.10},
    4: {"Equity": 0.65, "Debt": 0.20, "Gold": 0.10, "Savings": 0.05},
    5: {"Equity": 0.75, "Debt": 0.10, "Gold": 0.10, "Savings": 0.05},
}

# ============================================================
# RETIREMENT CORPUS ENGINES (CORRECTED)
# ============================================================
def required_corpus_fd(monthly_expense_today, years_to_ret, retirement_years):
    annual_at_ret = monthly_expense_today * 12 * ((1 + INFLATION) ** years_to_ret)

    def survives(C):
        for _ in range(retirement_years):
            C = C + C * POST_RET_RETURN - annual_at_ret
            if C < 0:
                return False
        return True

    lo, hi = 0, 1e11
    for _ in range(100):
        mid = (lo + hi) / 2
        if survives(mid):
            hi = mid
        else:
            lo = mid
    return hi


def required_corpus_inflation(monthly_expense_today, years_to_ret, retirement_years):
    annual_at_ret = monthly_expense_today * 12 * ((1 + INFLATION) ** years_to_ret)

    def survives(C):
        E = annual_at_ret
        for _ in range(retirement_years):
            C = C * (1 + POST_RET_RETURN) - E
            if C < 0:
                return False
            E *= (1 + INFLATION)
        return True

    lo, hi = 0, 1e11
    for _ in range(100):
        mid = (lo + hi) / 2
        if survives(mid):
            hi = mid
        else:
            lo = mid
    return hi

# ============================================================
# SIP + RISK ENGINES
# ============================================================
def portfolio_return(risk):
    return sum(RISK_ALLOC[risk][a] * ASSET_RETURNS[a] for a in ASSET_RETURNS)


def required_monthly_sip(required_corpus, current_savings, years, annual_return):
    lo, hi = 0, 300_000
    for _ in range(100):
        mid = (lo + hi) / 2
        C = current_savings
        for _ in range(years):
            C = C * (1 + annual_return) + 12 * mid
        if C >= required_corpus:
            hi = mid
        else:
            lo = mid
    return int(hi)


def min_start_sip_for_overshoot(required_sip, years, stepup, overshoot_factor=1.10):
    lo, hi = 0, required_sip
    for _ in range(60):
        mid = (lo + hi) / 2
        sip = mid
        for _ in range(years):
            sip = min(sip * (1 + stepup), required_sip * overshoot_factor)
        if sip >= required_sip * overshoot_factor:
            hi = mid
        else:
            lo = mid
    return int(hi)


def system_risk_level(current_age, retirement_age, is_behind):
    years = retirement_age - current_age
    base = 4 if years > 25 else 3 if years > 15 else 2
    if is_behind:
        base = min(5, base + 1)
    return base


def blended_risk(user_risk, system_risk):
    return max(1, min(5, round(0.6 * user_risk + 0.4 * system_risk)))

# ============================================================
# HEADER
# ============================================================
st.markdown("## Retirement Simulator")
st.markdown("Understand how much money you’ll need for retirement — and how to realistically get there.")
st.divider()

# ============================================================
# INPUTS
# ============================================================
col_inputs, col_info = st.columns([1, 1])

with col_inputs:
    with st.container(border=True):
        current_age = st.number_input("Current age", min_value=0, value=25)
        retirement_age = st.number_input("Planned retirement age", min_value=current_age + 1, value=55)

        monthly_expense = st.number_input(
            "Desired monthly expense (today’s value)",
            step=1000,
            value=100000
        )
        st.markdown(
            "<div class='small-note'>This amount is inflated till retirement age.</div>",
            unsafe_allow_html=True
        )

        retirement_style = st.radio(
            "Retirement spending style",
            [
                "Fixed Deposit (nominal spending, corpus reduces)",
                "Inflation-protected (real spending)"
            ]
        )

        if retirement_style.startswith("Fixed"):
            st.markdown(
                "<div class='small-note'>After retirement, withdrawals stay fixed in rupee terms. "
                "Purchasing power reduces over time.</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div class='small-note'>After retirement, withdrawals increase every year "
                "to preserve purchasing power.</div>",
                unsafe_allow_html=True
            )

        current_monthly_investment = st.number_input("Current monthly investment", step=1000, value=50000)
        current_savings = st.number_input("Retirement savings accumulated so far", step=50000, value=0)
        user_risk = st.slider("Risk tolerance", 1, 5, 3)

        calculate = st.button("Calculate my retirement plan", use_container_width=True)

# ============================================================
# CALCULATION
# ============================================================
if calculate:
    years_to_ret = retirement_age - current_age
    retirement_years = 90 - retirement_age

    required = (
        required_corpus_fd(monthly_expense, years_to_ret, retirement_years)
        if retirement_style.startswith("Fixed")
        else required_corpus_inflation(monthly_expense, years_to_ret, retirement_years)
    )

    progress = min(current_savings / required, 1.0)

    r_user = portfolio_return(user_risk)
    required_sip = required_monthly_sip(required, current_savings, years_to_ret, r_user)

    is_behind = current_monthly_investment < required_sip
    min_start_sip = min_start_sip_for_overshoot(required_sip, years_to_ret, MAX_SIP_GROWTH)
    can_recover = current_monthly_investment >= min_start_sip

    system_risk = system_risk_level(current_age, retirement_age, is_behind)
    final_risk = blended_risk(user_risk, system_risk)

    # ============================================================
    # RIGHT COLUMN – ASSUMPTIONS + PROGRESS
    # ============================================================
    with col_info:
        with st.container(border=True):
            st.markdown("### Our Assumptions")
            st.markdown("""
            • Inflation: 6%  
            • Post-retirement returns: 5%  
            • Life expectancy: 90  
            """)

        with st.container(border=True):
            st.markdown("### Your retirement journey so far")
            st.progress(progress)
            st.caption(f"You’ve saved ₹{current_savings:,} out of ₹{required/1e7:.2f} Cr")

        with st.container(border=True):
            st.markdown("### Your Retirement Requirement")
            st.markdown(f"**Required Corpus:** ₹{required/1e7:.2f} Cr")
            st.markdown(f"**Required Monthly Investment:** ₹{required_sip:,} / month")

            if is_behind:
                if not can_recover:
                    st.error(f"To recover, SIP must start at ₹{min_start_sip:,}/month and grow yearly.")
                else:
                    st.info("Temporary SIP overshoot is required to compensate for lost compounding.")
            else:
                st.success("At your current investment rate, you are on track.")

    # ============================================================
    # SIP PATH (OVERSHOOT)
    # ============================================================
    years = list(range(1, years_to_ret + 1))
    sip = current_monthly_investment
    catchup = []
    cap = 1.10 * required_sip

    for _ in years:
        catchup.append(int(sip))
        sip = min(sip * (1 + MAX_SIP_GROWTH), cap)

    df = pd.DataFrame({
        "Years till retirement": years,
        "Current SIP": [current_monthly_investment] * years_to_ret,
        "Required SIP": [required_sip] * years_to_ret,
        "Catch-up Path": catchup
    })

    if is_behind and can_recover:
        with st.expander("📉 How to close the gap (overshoot path)"):
            st.line_chart(df.set_index("Years till retirement"))

    # ============================================================
    # INVESTMENT ALLOCATION
    # ============================================================
    with st.container(border=True):
        st.markdown("### Where your monthly investment goes")
        st.markdown(
            f"""
            **Your risk choice:** {user_risk}  
            **System suggested risk:** {system_risk}  
            **Blended risk used:** {final_risk}
            """
        )

        alloc = RISK_ALLOC[final_risk]
        alloc_df = pd.DataFrame({
            "Asset Class": alloc.keys(),
            "Monthly Amount (₹)": [required_sip * v for v in alloc.values()]
        })

        c1, c2 = st.columns(2)
        with c1:
            pie = alt.Chart(alloc_df).mark_arc(innerRadius=50).encode(
                theta="Monthly Amount (₹):Q",
                color="Asset Class:N"
            )
            st.altair_chart(pie, use_container_width=True)

        with c2:
            st.dataframe(alloc_df, hide_index=True, use_container_width=True)

    # ============================================================
    # POST-RETIREMENT DE-INVESTMENT EXPLANATION
    # ============================================================
    with st.container(border=True):
        st.markdown("### How your retirement money is used")

        st.markdown("""
        **Suggested de-investment structure:**

        • **40–50% in Fixed Deposits / Liquid funds**  
          Covers near-term expenses with stability.

        • **30–40% in Debt instruments**  
          Provides moderate returns and refills FD bucket.

        • **10–30% in Growth assets**  
          Helps manage longevity risk.

        Withdrawals happen from the FD bucket, which is periodically refilled.
        As the corpus reduces, interest earned also naturally reduces.
        """)

    # ============================================================
    # FINAL EXPLANATION
    # ============================================================
    with st.container(border=True):
        st.markdown("### How to interpret the two retirement models")

        st.markdown("""
        **Fixed Deposit mode**  
        • Expenses are inflation-adjusted till retirement  
        • Withdrawals stay fixed after retirement  
        • Purchasing power reduces over time  
        • Requires a lower corpus  

        **Inflation-protected mode**  
        • Expenses are inflation-adjusted till retirement  
        • Withdrawals increase every year after retirement  
        • Purchasing power is preserved  
        • Requires a much higher corpus  

        Both approaches are valid — they reflect different retirement philosophies.
        """)
