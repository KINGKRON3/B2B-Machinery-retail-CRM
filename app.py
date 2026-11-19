import streamlit as st
from database import init_db
from seed_data import seed

st.set_page_config(page_title="B2B Machinery CRM", page_icon="🚜", layout="wide")

# Initialize DB and seed sample data on first run
init_db()
seed()

st.title("🚜 B2B Machinery Retail – CRM")
st.markdown("""
Welcome to the team CRM system. Select a module from the sidebar:
* **1 Dashboard:** Sales KPIs, pipeline overview, and inventory metrics
* **2 Customers:** B2B client companies, contacts, and equipment history
* **3 Pipeline:** Active quotes, deals, and negotiation stages
* **4 Machinery:** Equipment inventory, serial numbers, hours, and pricing
""")

st.info("💡 **Vibe Coding Rule:** Each page lives in its own file inside `pages/`. Only edit your assigned file to avoid GitHub merge conflicts.")
