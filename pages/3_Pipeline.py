import pandas as pd
import streamlit as st

from database import get_connection, init_db

# Make sure tables and demo data exist even if this page is opened first
init_db()

st.header("💼 Sales Pipeline & Deals")

STAGES = ["Lead", "Quote", "Negotiation", "Won", "Lost"]


def money(value) -> str:
    """Format a number as a euro amount."""
    return f"€{value:,.0f}"


def load_deals() -> pd.DataFrame:
    """All deals with customer and machine names."""
    conn = get_connection()
    try:
        return pd.read_sql_query(
            "SELECT d.id AS ID, d.title AS Deal, c.company_name AS Customer, "
            "m.model_name AS Machine, d.value AS Value, d.stage AS Stage "
            "FROM deals d "
            "LEFT JOIN customers c ON c.id = d.customer_id "
            "LEFT JOIN machines m ON m.id = d.machine_id "
            "ORDER BY d.id DESC",
            conn,
        )
    finally:
        conn.close()


def load_options(query: str) -> dict:
    """Return {id: label} for a dropdown."""
    conn = get_connection()
    try:
        return {row[0]: row[1] for row in conn.execute(query).fetchall()}
    finally:
        conn.close()


def mark_machine_sold(conn, machine_id, customer_id) -> None:
    """When a deal is Won, the machine becomes 'Sold' and is linked to the buying customer."""
    if machine_id is not None:
        conn.execute(
            "UPDATE machines SET status = 'Sold', customer_id = ? WHERE id = ?",
            (customer_id, machine_id),
        )


def create_deal(title, customer_id, machine_id, value, stage) -> None:
    """Insert a new deal."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO deals (title, customer_id, machine_id, value, stage) VALUES (?, ?, ?, ?, ?)",
            (title, customer_id, machine_id, value, stage),
        )
        if stage == "Won":
            mark_machine_sold(conn, machine_id, customer_id)
        conn.commit()
    finally:
        conn.close()


def update_deal(deal_id, stage, value) -> None:
    """Change a deal's stage and value."""
    conn = get_connection()
    try:
        conn.execute("UPDATE deals SET stage = ?, value = ? WHERE id = ?", (stage, value, deal_id))
        if stage == "Won":
            row = conn.execute(
                "SELECT machine_id, customer_id FROM deals WHERE id = ?", (deal_id,)
            ).fetchone()
            mark_machine_sold(conn, row["machine_id"], row["customer_id"])
        conn.commit()
    finally:
        conn.close()


if "pipeline_flash" in st.session_state:
    st.success(st.session_state.pop("pipeline_flash"))

deals = load_deals()
customers = load_options("SELECT id, company_name FROM customers ORDER BY company_name")
machines = load_options("SELECT id, model_name || ' (' || COALESCE(serial_number, 'no serial') || ')' FROM machines ORDER BY model_name")

tab_deals, tab_new, tab_update = st.tabs(["📋 Active Deals", "➕ New Deal", "🔄 Update Deal"])

# ---------------------------------------------------------------------------
# Deals table with stage filter
# ---------------------------------------------------------------------------
with tab_deals:
    chosen = st.multiselect("Filter by stage", STAGES, default=STAGES)
    shown = deals[deals["Stage"].isin(chosen)] if chosen else deals.iloc[0:0]
    m1, m2 = st.columns(2)
    m1.metric("Deals shown", len(shown))
    m2.metric("Total value", money(shown["Value"].sum()))
    display = shown.copy()
    display["Value"] = display["Value"].apply(lambda v: money(v) if pd.notna(v) else "—")
    display["Machine"] = display["Machine"].fillna("—")
    st.dataframe(display, width="stretch", hide_index=True)

# ---------------------------------------------------------------------------
# Create a deal
# ---------------------------------------------------------------------------
with tab_new:
    if not customers:
        st.info("Add a customer first (Customers page) before creating a deal.")
    else:
        with st.form("new_deal_form", clear_on_submit=True):
            title = st.text_input("Deal title *")
            customer_id = st.selectbox("Customer *", list(customers.keys()), format_func=lambda i: customers[i])
            machine_id = st.selectbox(
                "Machine (optional)", [None] + list(machines.keys()),
                format_func=lambda i: "— None —" if i is None else machines[i],
            )
            value = st.number_input("Deal value (EUR)", min_value=0.0, step=1000.0, format="%.0f")
            stage = st.selectbox("Stage", STAGES)
            created = st.form_submit_button("Create deal")
        if created:
            if not title.strip():
                st.error("Deal title is required.")
            else:
                create_deal(title.strip(), customer_id, machine_id, value, stage)
                st.session_state["pipeline_flash"] = f"Deal '{title.strip()}' was created."
                st.rerun()

# ---------------------------------------------------------------------------
# Update a deal's stage / value
# ---------------------------------------------------------------------------
with tab_update:
    if deals.empty:
        st.info("There are no deals to update yet.")
    else:
        labels = {int(r.ID): f"#{r.ID} · {r.Deal} ({r.Stage})" for r in deals.itertuples()}
        deal_id = st.selectbox("Select deal", list(labels.keys()), format_func=lambda i: labels[i])
        current = deals[deals["ID"] == deal_id].iloc[0]
        with st.form(f"update_deal_form_{deal_id}"):
            new_stage = st.selectbox("Stage", STAGES, index=STAGES.index(current["Stage"]))
            new_value = st.number_input(
                "Deal value (EUR)", min_value=0.0, step=1000.0, format="%.0f",
                value=float(current["Value"]) if pd.notna(current["Value"]) else 0.0,
            )
            saved = st.form_submit_button("Save changes")
        if saved:
            update_deal(int(deal_id), new_stage, new_value)
            note = " The linked machine was marked as Sold." if new_stage == "Won" else ""
            st.session_state["pipeline_flash"] = f"Deal #{deal_id} was updated.{note}"
            st.rerun()

# TODO for Role 2 (Casper): add a delete-deal action, a kanban-style stage board, deal notes and expected close dates.
