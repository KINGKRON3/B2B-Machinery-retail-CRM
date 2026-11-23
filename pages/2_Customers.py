import pandas as pd
import streamlit as st

from database import get_connection, init_db

st.set_page_config(page_title="Customers | B2B Machinery CRM", page_icon="🏢", layout="wide")
# Make sure tables and demo data exist even if this page is opened first
init_db()

st.header("🏢 B2B Customers & Contacts")


# ---------------------------------------------------------------------------
# Helper functions (all database access lives here; every connection is closed)
# ---------------------------------------------------------------------------
def load_customers() -> pd.DataFrame:
    """Return all customers as a DataFrame."""
    conn = get_connection()
    try:
        return pd.read_sql_query(
            "SELECT id, company_name, contact_person, email, phone, industry "
            "FROM customers ORDER BY company_name",
            conn,
        )
    finally:
        conn.close()


def add_customer(company, contact, email, phone, industry) -> None:
    """Insert a new customer row."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO customers (company_name, contact_person, email, phone, industry) "
            "VALUES (?, ?, ?, ?, ?)",
            (company, contact, email, phone, industry),
        )
        conn.commit()
    finally:
        conn.close()


def update_customer(customer_id, company, contact, email, phone, industry) -> None:
    """Update an existing customer row."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE customers SET company_name = ?, contact_person = ?, email = ?, "
            "phone = ?, industry = ? WHERE id = ?",
            (company, contact, email, phone, industry, customer_id),
        )
        conn.commit()
    finally:
        conn.close()


def load_customer_machines(customer_id) -> pd.DataFrame:
    """Machines linked to a customer (reserved or sold to them)."""
    conn = get_connection()
    try:
        return pd.read_sql_query(
            "SELECT model_name AS Model, serial_number AS 'Serial Number', "
            "operating_hours AS 'Operating Hours', price AS Price, status AS Status "
            "FROM machines WHERE customer_id = ? ORDER BY model_name",
            conn,
            params=(customer_id,),
        )
    finally:
        conn.close()


def load_customer_deals(customer_id) -> pd.DataFrame:
    """Deals of a customer, including the machine model (if any)."""
    conn = get_connection()
    try:
        return pd.read_sql_query(
            "SELECT d.title AS Title, m.model_name AS Machine, d.value AS Value, d.stage AS Stage "
            "FROM deals d LEFT JOIN machines m ON m.id = d.machine_id "
            "WHERE d.customer_id = ? ORDER BY d.id DESC",
            conn,
            params=(customer_id,),
        )
    finally:
        conn.close()


def clean(value) -> str:
    """Trim whitespace; return an empty string for None."""
    return (value or "").strip()


def money(value) -> str:
    """Format a number as a euro amount."""
    return f"€{value:,.0f}"


# Show a success message that was stored before st.rerun()
if "customer_flash" in st.session_state:
    st.success(st.session_state.pop("customer_flash"))

customers = load_customers()

tab_list, tab_add, tab_edit, tab_history = st.tabs(
    ["📋 Customer List", "➕ Add Customer", "✏️ Edit Customer", "🚜 Machine & Deal History"]
)

# ---------------------------------------------------------------------------
# Tab 1: search & filter
# ---------------------------------------------------------------------------
with tab_list:
    col_search, col_industry = st.columns([2, 1])
    search = col_search.text_input(
        "🔍 Search", placeholder="Company, contact person, email or phone"
    ).strip().lower()
    industries = sorted(i for i in customers["industry"].dropna().unique() if i)
    selected_industry = col_industry.selectbox("Industry", ["All industries"] + industries)

    filtered = customers.copy()
    if selected_industry != "All industries":
        filtered = filtered[filtered["industry"] == selected_industry]
    if search:
        searchable = (
            filtered[["company_name", "contact_person", "email", "phone"]]
            .fillna("")
            .astype(str)
            .agg(" ".join, axis=1)
            .str.lower()
        )
        filtered = filtered[searchable.str.contains(search, regex=False)]

    st.caption(f"Showing {len(filtered)} of {len(customers)} customers")
    st.dataframe(
        filtered.rename(
            columns={
                "id": "ID",
                "company_name": "Company",
                "contact_person": "Contact Person",
                "email": "Email",
                "phone": "Phone",
                "industry": "Industry",
            }
        ),
        width="stretch",
        hide_index=True,
    )

# ---------------------------------------------------------------------------
# Tab 2: add customer
# ---------------------------------------------------------------------------
with tab_add:
    with st.form("add_customer_form", clear_on_submit=True):
        company = st.text_input("Company name *")
        contact = st.text_input("Contact person")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        industry = st.text_input("Industry", placeholder="e.g. Forestry, Mining & Quarrying")
        submitted = st.form_submit_button("Add customer")

    if submitted:
        if not clean(company):
            st.error("Company name is required.")
        else:
            add_customer(clean(company), clean(contact), clean(email), clean(phone), clean(industry))
            st.session_state["customer_flash"] = f"Customer '{clean(company)}' was added."
            st.rerun()

# ---------------------------------------------------------------------------
# Tab 3: edit customer
# ---------------------------------------------------------------------------
with tab_edit:
    if customers.empty:
        st.info("No customers yet. Add one in the 'Add Customer' tab.")
    else:
        names = dict(zip(customers["id"], customers["company_name"]))
        edit_id = st.selectbox(
            "Select customer",
            options=list(names.keys()),
            format_func=lambda cid: names[cid],
            key="edit_customer_select",
        )
        row = customers[customers["id"] == edit_id].iloc[0]

        # The key includes the customer id so the fields reset when another customer is picked
        with st.form(f"edit_customer_form_{edit_id}"):
            e_company = st.text_input("Company name *", value=clean(row["company_name"]))
            e_contact = st.text_input("Contact person", value=clean(row["contact_person"]))
            e_email = st.text_input("Email", value=clean(row["email"]))
            e_phone = st.text_input("Phone", value=clean(row["phone"]))
            e_industry = st.text_input("Industry", value=clean(row["industry"]))
            saved = st.form_submit_button("Save changes")

        if saved:
            if not clean(e_company):
                st.error("Company name is required.")
            else:
                update_customer(
                    int(edit_id), clean(e_company), clean(e_contact),
                    clean(e_email), clean(e_phone), clean(e_industry),
                )
                st.session_state["customer_flash"] = f"Customer '{clean(e_company)}' was updated."
                st.rerun()

# ---------------------------------------------------------------------------
# Tab 4: machine & deal history
# ---------------------------------------------------------------------------
with tab_history:
    if customers.empty:
        st.info("No customers yet. Add one in the 'Add Customer' tab.")
    else:
        names = dict(zip(customers["id"], customers["company_name"]))
        hist_id = st.selectbox(
            "Select customer",
            options=list(names.keys()),
            format_func=lambda cid: names[cid],
            key="history_customer_select",
        )
        info = customers[customers["id"] == hist_id].iloc[0]
        st.markdown(
            f"**{info['company_name']}** · {clean(info['contact_person']) or '—'} · "
            f"{clean(info['email']) or '—'} · {clean(info['phone']) or '—'} · "
            f"{clean(info['industry']) or '—'}"
        )

        machines_df = load_customer_machines(int(hist_id))
        deals_df = load_customer_deals(int(hist_id))

        m1, m2, m3 = st.columns(3)
        m1.metric("Machines", len(machines_df))
        m2.metric("Deals", len(deals_df))
        won_value = deals_df.loc[deals_df["Stage"] == "Won", "Value"].sum() if not deals_df.empty else 0
        m3.metric("Won deal value", money(won_value))

        st.subheader("Machines")
        if machines_df.empty:
            st.info("No machines linked to this customer.")
        else:
            machines_df["Price"] = machines_df["Price"].apply(lambda v: money(v) if pd.notna(v) else "—")
            st.dataframe(machines_df, width="stretch", hide_index=True)

        st.subheader("Deals")
        if deals_df.empty:
            st.info("No deals for this customer.")
        else:
            deals_df["Value"] = deals_df["Value"].apply(lambda v: money(v) if pd.notna(v) else "—")
            deals_df["Machine"] = deals_df["Machine"].fillna("—")
            st.dataframe(deals_df, width="stretch", hide_index=True)

# TODO for Role 1 (Arttu): add delete-customer (with a check for linked machines/deals), customer notes, and CSV export of the filtered list.
