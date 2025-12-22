import streamlit as st
import pandas as pd
import altair as alt

# ============================================================
# UI SCALE (UNCHANGED)
# ============================================================
st.markdown("""
<style>
html, body, [class*="css"] { font-size: 17px; }
h1 { font-size: 2.4rem; }
h2 { font-size: 1.9rem; }
h3 { font-size: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONSTANTS (LOCKED)
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
# CORE ENGINES (LOCKED & VERIFIED)
# ============================================================
def required_corpus(monthly_expense, years_to_ret, retirement_years):
    annual = monthly_expense * 12
    expense_at_ret = annual * ((1 + INFLATION) ** years_to_ret)

    def survives(C):
        E = expense_at_ret
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


def portfolio_return(risk):
    return sum(
        RISK_ALLOC[risk][a] * ASSET_RETURNS[a]
        for a in ASSET_RETURNS
    )


def required_monthly_sip(required_corpus, current_savings, years, annual_return):
    lo, hi = 0, 200_000
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

# ============================================================
# NEW: SYSTEM RISK + BLENDED RISK (RULE-BASED)
# ============================================================
def system_risk_level(current_age, retirement_age, is_behind):
    years_to_ret = retirement_age - current_age

    if years_to_ret > 25:
        base = 4
    elif years_to_ret > 15:
        base = 3
    else:
        base = 2

    if is_behind:
        base = min(5, base + 1)

    return base


def blended_risk(user_risk, system_risk):
    return max(1, min(5, round(0.6 * user_risk + 0.4 * system_risk)))

# ============================================================
# PAGE HEADER
# ============================================================
st.markdown("## Retirement Simulator")
st.markdown(
    "Understand how much money you’ll need for retirement — "
    "and how to realistically get there."
)
st.divider()

# ============================================================
# INPUTS
# ============================================================
col_inputs, col_info = st.columns([1, 1])

with col_inputs:
    with st.container(border=True):
        current_age = st.number_input("Current age", min_value=0, value=45)
        retirement_age = st.number_input(
            "Planned retirement age", min_value=current_age + 1, value=60
        )

        monthly_expense = st.number_input(
            "Expected monthly expense after retirement",
            min_value=0, step=1000, value=24000
        )

        current_monthly_investment = st.number_input(
            "Current monthly investment",
            min_value=0, step=1000, value=70000
        )

        current_savings = st.number_input(
            "Retirement savings accumulated so far",
            min_value=0, step=50000, value=500000
        )

        user_risk = st.slider("Risk tolerance", 1, 5, 2)

        calculate = st.button("Calculate my retirement plan", use_container_width=True)
        st.caption("You can adjust inputs anytime and recalculate.")

# ============================================================
# CALCULATION
# ============================================================
if calculate:
    years_to_ret = retirement_age - current_age
    retirement_years = 90 - retirement_age

    required = required_corpus(
        monthly_expense, years_to_ret, retirement_years
    )

    progress_ratio = min(current_savings / required, 1.0)

    # Required SIP using USER risk return
    r_user = portfolio_return(user_risk)
    required_sip = required_monthly_sip(
        required, current_savings, years_to_ret, r_user
    )

    is_behind = current_monthly_investment < required_sip

    # NEW: system + blended risk
    system_risk = system_risk_level(
        current_age, retirement_age, is_behind
    )
    final_risk = blended_risk(user_risk, system_risk)

    # ----------------------------
    # RIGHT COLUMN – ASSUMPTIONS + PROGRESS
    # ----------------------------
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
            st.markdown(
                f"You’ve saved **₹{current_savings:,}** out of "
                f"**₹{required/1e7:.2f} Cr** so far"
            )
            st.progress(progress_ratio)
            st.caption(
                f"Progress so far: {int(progress_ratio*100)}% of your retirement goal"
            )

    # ----------------------------
    # REQUIREMENT BOX
    # ----------------------------
    with col_info:
        with st.container(border=True):
            st.markdown("### Your Retirement Requirement")

            st.markdown(
                f"""
                <div style="margin-bottom:10px;">
                    <div style="font-size:14px; color:#9ca3af;">Required Corpus</div>
                    <div style="font-size:36px; font-weight:700; color:#34d399;">
                        ₹{required/1e7:.2f} Cr
                    </div>
                </div>

                <div style="margin-bottom:6px;">
                    <div style="font-size:14px; color:#9ca3af;">
                        Required Monthly Investment
                    </div>
                    <div style="font-size:28px; font-weight:600; color:#34d399;">
                        ₹{required_sip:,} / month
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if is_behind:
                st.markdown(
                    """
                    <div style="
                        margin-top:8px;
                        margin-bottom:12px;
                        padding:8px 10px;
                        background-color:#3f1d1d;
                        color:#fca5a5;
                        font-size:13px;
                        border-radius:6px;
                    ">
                    You are currently behind your target.
                    <b> Click below to see how you can catch up.</b>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # ============================================================
    # SIP PATH
    # ============================================================
    years = list(range(1, years_to_ret + 1))

    current_line = [current_monthly_investment] * years_to_ret
    required_line = [required_sip] * years_to_ret

    sip = current_monthly_investment
    catchup = []
    for _ in years:
        catchup.append(int(sip))
        if sip < required_sip:
            sip = min(sip * (1 + MAX_SIP_GROWTH), required_sip)

    df = pd.DataFrame({
        "Years till retirement": years,
        "Current SIP": current_line,
        "Required SIP (Target)": required_line,
        "Catch-up Path": catchup
    })

    if is_behind:
        with st.expander("📉 How to close the gap (recommended path)", expanded=False):
            st.line_chart(
                df.set_index("Years till retirement"),
                use_container_width=True
            )
    else:
        st.success(
            "At your current investment rate, you are on track to meet "
            "your retirement goal."
        )

    # ============================================================
    # INVESTMENT ALLOCATION (BLENDED RISK)
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
            "Monthly Amount (₹)": [
                required_sip * v for v in alloc.values()
            ]
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
    # POST-RETIREMENT WITHDRAWAL EXPLANATION
    # ============================================================
    with st.container(border=True):
        st.markdown("### How your retirement money is actually used")

        st.markdown("""
    After retirement, your money is **not withdrawn all at once**.

    The system assumes a **bucket-based withdrawal approach**:

    • **Short-term bucket (0–3 years):**  
      Kept in **fixed deposits / liquid funds** for regular yearly expenses.

    • **Medium-term bucket (4–10 years):**  
      Parked in **debt-oriented instruments** to beat inflation with stability.

    • **Long-term bucket (10+ years):**  
      Remains invested in **growth assets** to support later years.

    Each year:
                    
    • One year’s expense is withdrawn from the safe bucket  
    • Buckets are **refilled gradually**, not liquidated fully  
    • This helps earn returns while keeping withdrawals predictable
    """)

