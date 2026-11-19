import streamlit as st
import pandas as pd
from database import get_connection

st.header("🏢 B2B Customers & Contacts")

conn = get_connection()
df = pd.read_sql_query("SELECT * FROM customers", conn)
conn.close()

st.dataframe(df, use_container_width=True)

st.warning("🚧 **Role 1 Workspace:** Add a form to create new customers, search/filter by industry, and view machines owned by each customer.")
