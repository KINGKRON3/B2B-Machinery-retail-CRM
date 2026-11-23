import sqlite3

import pandas as pd
import streamlit as st

from database import get_connection, init_db

# Make sure tables and demo data exist even if this page is opened first
init_db()

st.header("🚜 Machinery Inventory & Fleet")

STATUSES = ["In Stock", "Reserved", "Sold"]


def money(value) -> str:
    """Format a number as a euro amount."""
    return f"€{value:,.0f}"


def load_machines() -> pd.DataFrame:
    """All machines with the customer they are assigned to (if any)."""
    conn = get_connection()
    try:
        return pd.read_sql_query(
            "SELECT m.id AS ID, m.model_name AS Model, m.serial_number AS 'Serial Number', "
            "m.operating_hours AS Hours, m.price AS Price, m.status AS Status, "
            "c.company_name AS 'Assigned Customer' "
            "FROM machines m LEFT JOIN customers c ON c.id = m.customer_id "
            "ORDER BY m.id",
            conn,
        )
    finally:
        conn.close()


def add_machine(model, serial, hours, price, status) -> bool:
    """Insert a machine. Returns False if the serial number already exists."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO machines (model_name, serial_number, operating_hours, price, status) "
            "VALUES (?, ?, ?, ?, ?)",
            (model, serial or None, hours, price, status),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def update_machine(machine_id, hours, price, status) -> None:
    """Update operating hours, price and status of a machine."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE machines SET operating_hours = ?, price = ?, status = ? WHERE id = ?",
            (hours, price, status, machine_id),
        )
        conn.commit()
    finally:
        conn.close()


if "machinery_flash" in st.session_state:
    st.success(st.session_state.pop("machinery_flash"))

machines = load_machines()
tab_list, tab_add, tab_update = st.tabs(["📋 Inventory", "➕ Add Machine", "✏️ Update Machine"])

# ---------------------------------------------------------------------------
# Inventory table with status filter
# ---------------------------------------------------------------------------
with tab_list:
    status_filter = st.selectbox("Filter by status", ["All"] + STATUSES)
    shown = machines if status_filter == "All" else machines[machines["Status"] == status_filter]
    m1, m2 = st.columns(2)
    m1.metric("Machines shown", len(shown))
    m2.metric("Total value", money(shown["Price"].sum()))
    display = shown.copy()
    display["Price"] = display["Price"].apply(lambda v: money(v) if pd.notna(v) else "—")
    display["Assigned Customer"] = display["Assigned Customer"].fillna("—")
    st.dataframe(display, width="stretch", hide_index=True)

# ---------------------------------------------------------------------------
# Add a machine
# ---------------------------------------------------------------------------
with tab_add:
    with st.form("add_machine_form", clear_on_submit=True):
        model = st.text_input("Model name *")
        serial = st.text_input("Serial number", help="Must be unique")
        hours = st.number_input("Operating hours", min_value=0, step=50)
        price = st.number_input("Price (EUR)", min_value=0.0, step=1000.0, format="%.0f")
        status = st.selectbox("Status", STATUSES)
        added = st.form_submit_button("Add machine")
    if added:
        if not model.strip():
            st.error("Model name is required.")
        elif not add_machine(model.strip(), serial.strip(), int(hours), price, status):
            st.error(f"A machine with serial number '{serial.strip()}' already exists.")
        else:
            st.session_state["machinery_flash"] = f"Machine '{model.strip()}' was added."
            st.rerun()

# ---------------------------------------------------------------------------
# Update hours / price / status
# ---------------------------------------------------------------------------
with tab_update:
    if machines.empty:
        st.info("No machines in the inventory yet.")
    else:
        labels = {int(r.ID): f"#{r.ID} · {r.Model}" for r in machines.itertuples()}
        machine_id = st.selectbox("Select machine", list(labels.keys()), format_func=lambda i: labels[i])
        current = machines[machines["ID"] == machine_id].iloc[0]
        with st.form(f"update_machine_form_{machine_id}"):
            new_hours = st.number_input(
                "Operating hours", min_value=0, step=50,
                value=int(current["Hours"]) if pd.notna(current["Hours"]) else 0,
            )
            new_price = st.number_input(
                "Price (EUR)", min_value=0.0, step=1000.0, format="%.0f",
                value=float(current["Price"]) if pd.notna(current["Price"]) else 0.0,
            )
            new_status = st.selectbox("Status", STATUSES, index=STATUSES.index(current["Status"]))
            saved = st.form_submit_button("Save changes")
        if saved:
            update_machine(int(machine_id), int(new_hours), new_price, new_status)
            st.session_state["machinery_flash"] = f"Machine #{machine_id} was updated."
            st.rerun()

# TODO for Role 3 (Hugo): add delete-machine, assign-to-customer, a search box, and a link to each machine's service history.
