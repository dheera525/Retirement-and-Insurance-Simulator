import streamlit as st
from dataclasses import dataclass
from typing import List, Optional

# ============================================================
# DATA MODEL
# ============================================================
@dataclass
class InsuranceInputs:
    age: int
    annual_income: float
    dependents: int
    existing_life_cover: float
    existing_health_cover: float
    city_tier: str
    lifestyle_risks: Optional[List[str]] = None


# ============================================================
# CORE LOGIC (LOCKED)
# ============================================================
def calculate_required_life_cover(inputs: InsuranceInputs) -> float:
    if inputs.dependents >= 3:
        multiplier = 15
    elif inputs.dependents >= 1:
        multiplier = 12
    else:
        multiplier = 10
    return inputs.annual_income * multiplier


def calculate_required_health_cover(inputs: InsuranceInputs) -> float:
    age = inputs.age
    dependents = inputs.dependents
    city_tier = inputs.city_tier
    lifestyle = inputs.lifestyle_risks or []

    if age < 30:
        base_cover = 1_000_000
    elif age <= 45:
        base_cover = 1_500_000
    else:
        base_cover = 2_500_000

    if dependents >= 2:
        base_cover += 500_000

    if city_tier == "Tier_1":
        base_cover += 500_000
    elif city_tier == "Tier_2":
        base_cover += 250_000

    if "smoking" in lifestyle:
        base_cover += 500_000
    if "sedentary" in lifestyle:
        base_cover += 250_000
    if "high_stress" in lifestyle:
        base_cover += 250_000

    return base_cover


def calculate_insurance_gap(inputs: InsuranceInputs) -> dict:
    required_life = calculate_required_life_cover(inputs)
    required_health = calculate_required_health_cover(inputs)

    life_gap = max(0, required_life - inputs.existing_life_cover)
    health_gap = max(0, required_health - inputs.existing_health_cover)

    return {
        "required_life": required_life,
        "required_health": required_health,
        "life_gap": life_gap,
        "health_gap": health_gap,
        "life_status": "Adequate" if life_gap == 0 else "Underinsured",
        "health_status": "Adequate" if health_gap == 0 else "Underinsured"
    }


def estimate_life_premium(life_gap: float, age: int):
    if life_gap <= 0:
        return (0, 0)

    units = life_gap / 1_000_000

    if age < 30:
        rate = (500, 800)
    elif age <= 45:
        rate = (800, 1200)
    else:
        rate = (1500, 2500)

    return round(units * rate[0]), round(units * rate[1])


def estimate_health_premium(health_gap: float, age: int):
    if health_gap <= 0:
        return (0, 0)

    units = health_gap / 1_000_000

    if age < 30:
        rate = (6000, 8000)
    elif age <= 45:
        rate = (8000, 12000)
    else:
        rate = (15000, 25000)

    return round(units * rate[0]), round(units * rate[1])


# ============================================================
# PAGE UI
# ============================================================
st.set_page_config(page_title="Insurance Simulator", layout="wide")

st.markdown("## 🛡 Insurance Simulator")
st.caption("Check whether your life and health insurance are actually sufficient.")
st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    with st.container(border=True):
        age = st.number_input("Age", 18, 80, 30)
        annual_income = st.number_input("Annual Income (₹)", 0, step=100000)
        dependents = st.number_input("Number of Dependents", 0, 10, 0)

        existing_life = st.number_input("Existing Life Cover (₹)", 0, step=500000)
        existing_health = st.number_input("Existing Health Cover (₹)", 0, step=500000)

        city_tier = st.selectbox("City Tier", ["Tier_1", "Tier_2", "Tier_3"])
        lifestyle = st.multiselect(
            "Lifestyle Risk Factors",
            ["smoking", "sedentary", "high_stress"]
        )

        calculate = st.button("Check My Insurance", use_container_width=True)


if calculate:
    inputs = InsuranceInputs(
        age=age,
        annual_income=annual_income,
        dependents=dependents,
        existing_life_cover=existing_life,
        existing_health_cover=existing_health,
        city_tier=city_tier,
        lifestyle_risks=lifestyle
    )

    result = calculate_insurance_gap(inputs)

    with col2:
        with st.container(border=True):
            st.markdown("### Coverage Summary")

            st.metric("Required Life Cover", f"₹{result['required_life']:,}")
            st.metric("Life Insurance Gap", f"₹{result['life_gap']:,}", result["life_status"])

            low, high = estimate_life_premium(result["life_gap"], age)
            if low > 0:
                st.caption(f"Estimated Life Premium: ₹{low} – ₹{high} / year")

            st.divider()

            st.metric("Required Health Cover", f"₹{result['required_health']:,}")
            st.metric("Health Insurance Gap", f"₹{result['health_gap']:,}", result["health_status"])

            low, high = estimate_health_premium(result["health_gap"], age)
            if low > 0:
                st.caption(f"Estimated Health Premium: ₹{low} – ₹{high} / year")
