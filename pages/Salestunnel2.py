import streamlit as st
import pandas as pd
from database import get_connection

st.header("💼 Sales Pipeline & Deals")

conn = get_connection()
query = """
SELECT deals.id, deals.title AS Deal, customers.company_name AS Customer, 
       machines.model_name AS Machine, deals.value AS Value_EUR, deals.stage AS Stage
FROM deals
LEFT JOIN customers ON deals.customer_id = customers.id
LEFT JOIN machines ON deals.machine_id = machines.id
"""
df = pd.read_sql_query(query, conn)
conn.close()

st.dataframe(df, use_container_width=True)

st.warning("🚧 **Role 2 Workspace:** Add a form to create new deals, update deal stages, and automatically mark the machine as 'Sold' when a deal reaches 'Won'.")
