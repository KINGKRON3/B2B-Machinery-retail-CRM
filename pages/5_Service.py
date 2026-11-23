import pandas as pd
import streamlit as st

from database import get_connection, init_db

# Make sure tables and demo data exist even if this page is opened first
init_db()

st.header("🔧 Service, Maintenance & Warranty")

# The service_logs table is created by init_db() in database.py
conn = get_connection()
try:
    query = """
    SELECT service_logs.id, machines.model_name AS Machine, machines.serial_number AS Serial_Number,
           service_logs.service_date AS Date, service_logs.service_type AS Type,
           service_logs.description AS Description, service_logs.cost AS Cost_EUR,
           service_logs.status AS Status
    FROM service_logs
    LEFT JOIN machines ON service_logs.machine_id = machines.id
    ORDER BY service_logs.service_date DESC
    """
    df = pd.read_sql_query(query, conn)
finally:
    conn.close()

st.metric("Total service costs", f"€{df['Cost_EUR'].sum():,.0f}")
st.dataframe(df, width="stretch", hide_index=True)

# TODO for Role 5 (Daniel): add a form to log maintenance/repairs for a selected machine (INSERT INTO service_logs),
# update service statuses ('Scheduled' -> 'Completed'), and show service costs per machine.
