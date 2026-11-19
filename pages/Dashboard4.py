import streamlit as st
import pandas as pd
from database import get_connection

st.header("📊 Executive Sales Dashboard")

conn = get_connection()
deals_df = pd.read_sql_query("SELECT * FROM deals", conn)
machines_df = pd.read_sql_query("SELECT * FROM machines", conn)
conn.close()

col1, col2, col3 = st.columns(3)
open_pipeline = deals_df[~deals_df['stage'].isin(['Won', 'Lost'])]['value'].sum()
won_revenue = deals_df[deals_df['stage'] == 'Won']['value'].sum()
in_stock_count = len(machines_df[machines_df['status'] == 'In Stock'])

col1.metric("Open Pipeline (€)", f"{open_pipeline:,.0f} €")
col2.metric("Closed Won Revenue (€)", f"{won_revenue:,.0f} €")
col3.metric("Machines In Stock", in_stock_count)

st.subheader("Pipeline Value by Stage")
if not deals_df.empty:
    stage_summary = deals_df.groupby("stage")["value"].sum()
    st.bar_chart(stage_summary)

st.warning("🚧 **Role 4 Workspace:** Expand with interactive Plotly charts, inventory valuation, and filters.")
