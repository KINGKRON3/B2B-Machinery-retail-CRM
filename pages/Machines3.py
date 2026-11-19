import streamlit as st
import pandas as pd
from database import get_connection

st.header("🚜 Machinery Inventory & Fleet")

conn = get_connection()
query = """
SELECT machines.id, machines.model_name AS Model, machines.serial_number AS Serial_Number,
       machines.operating_hours AS Hours, machines.price AS Price_EUR, 
       machines.status AS Status, customers.company_name AS Assigned_Customer
FROM machines
LEFT JOIN customers ON machines.customer_id = customers.id
"""
df = pd.read_sql_query(query, conn)
conn.close()

st.dataframe(df, use_container_width=True)

st.warning("🚧 **Role 3 Workspace:** Add a form to register new machinery, update operating hours/prices/status, and filter by stock status.")
