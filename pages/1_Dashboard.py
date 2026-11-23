import pandas as pd
import plotly.express as px
import streamlit as st

from database import get_connection, init_db

# Make sure tables and demo data exist even if this page is opened first
init_db()

st.header("📊 Executive Sales Dashboard")

STAGES = ["Lead", "Quote", "Negotiation", "Won", "Lost"]
STATUSES = ["In Stock", "Reserved", "Sold"]
STAGE_COLORS = {
    "Lead": "#7f8c9b", "Quote": "#3b82c4", "Negotiation": "#e08e2b",
    "Won": "#2e9e5b", "Lost": "#c8453d",
}
STATUS_COLORS = {"In Stock": "#2e9e5b", "Reserved": "#e08e2b", "Sold": "#3b82c4"}


def money(value) -> str:
    """Format a number as a euro amount."""
    return f"€{value:,.0f}"


def load_table(query: str) -> pd.DataFrame:
    """Run a read-only query and always close the connection."""
    conn = get_connection()
    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


customers_df = load_table("SELECT id FROM customers")
deals_df = load_table("SELECT stage, value FROM deals")
machines_df = load_table("SELECT status, price FROM machines")

# ---------------------------------------------------------------------------
# KPI overview
# ---------------------------------------------------------------------------
fleet_value = machines_df.loc[machines_df["status"] == "In Stock", "price"].sum()
open_pipeline = deals_df.loc[deals_df["stage"].isin(["Lead", "Quote", "Negotiation"]), "value"].sum()
won_revenue = deals_df.loc[deals_df["stage"] == "Won", "value"].sum()
won_count = int((deals_df["stage"] == "Won").sum())
lost_count = int((deals_df["stage"] == "Lost").sum())
win_rate = f"{won_count / (won_count + lost_count):.0%}" if (won_count + lost_count) else "—"

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Customers", len(customers_df))
k2.metric("Fleet Value (In Stock)", money(fleet_value))
k3.metric("Open Pipeline", money(open_pipeline))
k4.metric("Won Revenue", money(won_revenue))
k5.metric("Win Rate", win_rate, help="Won deals divided by Won + Lost deals")

# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("Pipeline Value by Stage")
    by_stage = (
        deals_df.groupby("stage")["value"].sum().reindex(STAGES).fillna(0).reset_index()
        .rename(columns={"stage": "Stage", "value": "Value (EUR)"})
    )
    fig_stage = px.bar(
        by_stage, x="Stage", y="Value (EUR)", color="Stage",
        color_discrete_map=STAGE_COLORS, text_auto=",.0f",
    )
    fig_stage.update_layout(showlegend=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig_stage, width="stretch")

with right:
    st.subheader("Fleet Status Breakdown")
    if machines_df.empty:
        st.info("No machines in the inventory yet.")
    else:
        by_status = (
            machines_df.groupby("status").size().reindex(STATUSES).fillna(0).reset_index(name="Machines")
            .rename(columns={"status": "Status"})
        )
        fig_status = px.pie(
            by_status, names="Status", values="Machines", hole=0.5,
            color="Status", color_discrete_map=STATUS_COLORS,
        )
        fig_status.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig_status, width="stretch")

# TODO for Role 4 (Salla): add a date filter, revenue-by-industry chart, top customers by won value,
# and a service-cost KPI (service_logs.cost) to this dashboard.
