import pandas as pd
import streamlit as st

from database import get_connection, init_db, load_demo_data

st.set_page_config(page_title="B2B Machinery CRM", page_icon="🚜", layout="wide")

# Create tables; demo data is loaded automatically when the database is empty
init_db()

STAGES = ["Lead", "Quote", "Negotiation", "Won", "Lost"]


def money(value) -> str:
    """Format a number as a euro amount."""
    return f"€{value:,.0f}"


def load_kpis() -> dict:
    """Headline numbers for the overview."""
    conn = get_connection()
    try:
        return {
            "customers": conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0],
            "fleet_value": conn.execute(
                "SELECT COALESCE(SUM(price), 0) FROM machines WHERE status = 'In Stock'"
            ).fetchone()[0],
            "open_pipeline": conn.execute(
                "SELECT COALESCE(SUM(value), 0) FROM deals "
                "WHERE stage IN ('Lead', 'Quote', 'Negotiation')"
            ).fetchone()[0],
            "won_revenue": conn.execute(
                "SELECT COALESCE(SUM(value), 0) FROM deals WHERE stage = 'Won'"
            ).fetchone()[0],
        }
    finally:
        conn.close()


def load_deals_by_stage() -> pd.DataFrame:
    """Deal count and value per stage, always listing all 5 stages in order."""
    conn = get_connection()
    try:
        df = pd.read_sql_query(
            "SELECT stage AS Stage, COUNT(*) AS Deals, SUM(value) AS Value "
            "FROM deals GROUP BY stage",
            conn,
        )
    finally:
        conn.close()
    df = df.set_index("Stage").reindex(STAGES).fillna(0).reset_index()
    df["Deals"] = df["Deals"].astype(int)
    return df


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
st.title("🚜 B2B Machinery Retail – CRM")
st.caption("Demo overview · use the sidebar to open Customers, Pipeline, Machinery and the other modules.")

if "demo_flash" in st.session_state:
    st.success(st.session_state.pop("demo_flash"))

kpis = load_kpis()
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Customers", kpis["customers"])
k2.metric("Fleet Inventory Value", money(kpis["fleet_value"]), help="Total price of machines with status 'In Stock'")
k3.metric("Open Pipeline Value", money(kpis["open_pipeline"]), help="Deals in Lead, Quote or Negotiation")
k4.metric("Won Revenue", money(kpis["won_revenue"]), help="Deals in stage 'Won'")

st.subheader("Deals by Stage")
stage_df = load_deals_by_stage()
display_df = stage_df.copy()
display_df["Value"] = display_df["Value"].apply(money)
st.dataframe(display_df, width="stretch", hide_index=True)

# ---------------------------------------------------------------------------
# Reset demo data (two-step so it cannot be clicked by accident mid-demo)
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Demo Controls")
if not st.session_state.get("confirm_reset"):
    if st.button("🔄 Reset Demo Data"):
        st.session_state["confirm_reset"] = True
        st.rerun()
else:
    st.warning("This deletes ALL customers, machines, deals and service logs and restores the original demo data.")
    col_yes, col_no, _ = st.columns([1, 1, 4])
    if col_yes.button("Yes, reset", type="primary"):
        load_demo_data(force=True)
        st.session_state["confirm_reset"] = False
        st.session_state["demo_flash"] = "Demo data has been reset."
        st.rerun()
    if col_no.button("Cancel"):
        st.session_state["confirm_reset"] = False
        st.rerun()

# TODO for Role 1 (Arttu): add quick-link buttons to the other pages and a recent-activity feed.
