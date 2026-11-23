import streamlit as st
import pandas as pd
from database import get_connection

st.header("🔧 Service, Maintenance & Warranty")

conn = get_connection()
c = conn.cursor()

# Ensure table exists until added to database.py
c.execute('''CREATE TABLE IF NOT EXISTS service_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id INTEGER,
    service_date TEXT,
    description TEXT,
    cost REAL,
    status TEXT DEFAULT 'Scheduled',
    FOREIGN KEY (machine_id) REFERENCES machines (id)
)''')
conn.commit()

query = """
SELECT service_logs.id, machines.model_name AS Machine, machines.serial_number AS Serial_Number,
       service_logs.service_date AS Date, service_logs.description AS Description,
       service_logs.cost AS Cost_EUR, service_logs.status AS Status
FROM service_logs
LEFT JOIN machines ON service_logs.machine_id = machines.id
"""
df = pd.read_sql_query(query, conn)
conn.close()

st.dataframe(df, use_container_width=True)

st.warning("🚧 **Role 5 Workspace:** Add a form to log maintenance/repairs for a selected machine, update service statuses, and track total service costs.")
