import streamlit as st

st.set_page_config(
    page_title="Retirement & Insurance Simulator",
    layout="wide"
)

# ============================================================
# GLOBAL STYLE – MODERN FINTECH
# ============================================================
st.markdown("""
<style>
.block-container {
    max-width: 1050px;
}

/* =========================
   HERO
   ========================= */
.hero-title {
    font-size: 52px;            /* ↑ stronger first impression */
    font-weight: 800;
    letter-spacing: -0.025em;
    margin-bottom: 10px;
}

.hero-subtitle {
    font-size: 19px;            /* slightly larger but lighter */
    color: #9ca3af;
    max-width: 720px;
    margin-bottom: 18px;
}

.hero-hook {
    font-size: 15.5px;          /* smaller, calmer */
    color: #cbd5f5;
    font-style: italic;         /* visual break for the eye */
    margin-bottom: 30px;
}

/* =========================
   PRIMARY SECTION
   ========================= */
.primary-title {
    font-size: 30px;            /* clear section jump */
    font-weight: 700;
    margin-bottom: 8px;
}

.primary-desc {
    font-size: 16.5px;
    color: #9ca3af;
    max-width: 650px;
    line-height: 1.55;          /* easier reading */
    margin-bottom: 16px;
}

/* Supporting line */
.supporting-line {
    font-size: 14px;
    color: #94a3b8;
    margin-bottom: 14px;
}

/* =========================
   BUTTONS
   ========================= */
.stButton > button {
    padding: 14px;
    font-size: 16px;
    font-weight: 600;
}

/* =========================
   SECONDARY SECTION
   ========================= */
.secondary {
    margin-top: 56px;
}

.secondary-title {
    font-size: 22px;            /* intentionally smaller */
    font-weight: 600;
    margin-bottom: 4px;
}

.secondary-desc {
    font-size: 14.5px;
    color: #9ca3af;
    max-width: 600px;
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HERO
# ============================================================
st.markdown(
    """
    <div class="hero-title">
        Plan Your Financial Future
    </div>

    <div class="hero-subtitle">
        Find out if you’re actually on track for retirement — and exactly
        how to fix it if you’re not.
    </div>

    <div class="hero-hook">
        Most people don’t know whether their retirement plan will really work.
        This simulator shows you — clearly.
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# ============================================================
# PRIMARY ACTION — RETIREMENT
# ============================================================
st.markdown(
    """
    <div class="primary-title">
        📈 Retirement Readiness
    </div>

    <div class="primary-desc">
        In under 60 seconds, see whether your savings, SIPs, and risk level
        are enough to support your retirement — and what needs to change if
        they aren’t.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="supporting-line">No signup • No product pitching • Transparent assumptions</div>',
    unsafe_allow_html=True
)


if st.button("→ Start Retirement Planning", use_container_width=True):
    st.switch_page("pages/retirement.py")

# ============================================================
# SECONDARY ACTION — INSURANCE
# ============================================================
st.markdown('<div class="secondary">', unsafe_allow_html=True)

st.markdown(
    """
    <div class="primary-title">
        🛡 Insurance Adequacy
    </div>

    <div class="primary-desc">
        Already planning long term? Check whether your life and health insurance
        actually protect your family — or if there are hidden coverage gaps.
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown(
    '<div class="supporting-line">No signup • No product pitching • Transparent assumptions</div>',
    unsafe_allow_html=True
)

if st.button("Check Insurance Coverage →", use_container_width=True):
    st.switch_page("pages/insurance.py")

st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ============================================================
# TRUST FOOTER
# ============================================================
st.markdown(
    """
    **Built on transparent assumptions.  
    No hidden overrides. No product pushing.**
    """
)

st.caption(
    "This is an educational simulator. It does not provide financial advice."
)
