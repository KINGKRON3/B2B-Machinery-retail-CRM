from datetime import date

import pandas as pd
import streamlit as st

from database import get_connection, init_db

# Make sure tables and demo data exist even if this page is opened first
init_db()

st.header("📄 Documents")

DOC_TYPES = ["Quote", "Contract Summary"]


def money(value) -> str:
    """Format a number as a euro amount."""
    return f"€{value:,.2f}" if value is not None else "—"


def load_deals() -> list:
    """All deals (id + title + stage) for the dropdown."""
    conn = get_connection()
    try:
        return conn.execute("SELECT id, title, stage FROM deals ORDER BY id DESC").fetchall()
    finally:
        conn.close()


def load_deal_details(deal_id):
    """One deal joined with its customer and machine."""
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT d.id AS deal_id, d.title, d.value, d.stage, "
            "c.company_name, c.contact_person, c.email, c.phone, c.industry, "
            "m.model_name, m.serial_number, m.operating_hours, m.price AS list_price, m.status AS machine_status "
            "FROM deals d "
            "LEFT JOIN customers c ON c.id = d.customer_id "
            "LEFT JOIN machines m ON m.id = d.machine_id "
            "WHERE d.id = ?",
            (deal_id,),
        ).fetchone()
    finally:
        conn.close()


def build_summary(doc_type: str, d) -> str:
    """Plain-text quote / contract summary for one deal."""
    na = lambda v: v if v not in (None, "") else "—"
    hours = f"{d['operating_hours']:,} h" if d["operating_hours"] is not None else "—"
    lines = [
        f"{doc_type.upper()} - DEAL #{d['deal_id']}",
        f"Date: {date.today().isoformat()}",
        "=" * 50,
        "",
        "CUSTOMER",
        f"  Company:  {na(d['company_name'])}",
        f"  Contact:  {na(d['contact_person'])}",
        f"  Email:    {na(d['email'])}",
        f"  Phone:    {na(d['phone'])}",
        f"  Industry: {na(d['industry'])}",
        "",
        "MACHINE",
        f"  Model:           {na(d['model_name'])}",
        f"  Serial number:   {na(d['serial_number'])}",
        f"  Operating hours: {hours}",
        f"  List price:      {money(d['list_price'])}",
        f"  Status:          {na(d['machine_status'])}",
        "",
        "DEAL",
        f"  Title: {d['title']}",
        f"  Stage: {d['stage']}",
        f"  Value: {money(d['value'])}",
        "",
        "Prices exclude VAT, delivery and optional service contracts." if doc_type == "Quote"
        else "Subject to signed sales agreement, payment terms and warranty conditions.",
    ]
    return "\n".join(lines)


deals = load_deals()
if not deals:
    st.info("There are no deals yet. Create one on the Pipeline page.")
else:
    labels = {row["id"]: f"#{row['id']} · {row['title']} ({row['stage']})" for row in deals}
    col_deal, col_type = st.columns([3, 1])
    deal_id = col_deal.selectbox("Select deal", list(labels.keys()), format_func=lambda i: labels[i])
    doc_type = col_type.selectbox("Document type", DOC_TYPES)

    details = load_deal_details(deal_id)
    summary = build_summary(doc_type, details)

    st.subheader(f"{doc_type} preview")
    st.code(summary, language=None)

    # CSV version: one row per field so it opens cleanly in Excel
    csv_df = pd.DataFrame(
        {
            "Field": ["Document", "Date", "Deal ID", "Deal", "Stage", "Value (EUR)", "Company", "Contact",
                      "Email", "Phone", "Industry", "Machine", "Serial number", "Operating hours", "List price (EUR)"],
            "Value": [doc_type, date.today().isoformat(), details["deal_id"], details["title"], details["stage"],
                      details["value"], details["company_name"], details["contact_person"], details["email"],
                      details["phone"], details["industry"], details["model_name"], details["serial_number"],
                      details["operating_hours"], details["list_price"]],
        }
    )
    file_stem = f"{doc_type.lower().replace(' ', '_')}_deal_{deal_id}"
    d1, d2, _ = st.columns([1, 1, 4])
    d1.download_button("⬇️ Download .txt", summary, file_name=f"{file_stem}.txt", mime="text/plain")
    d2.download_button("⬇️ Download .csv", csv_df.to_csv(index=False), file_name=f"{file_stem}.csv", mime="text/csv")

# TODO for Role 6 (Nicolas): add PDF export, company logo/letterhead, customer-specific terms,
# and a documents history table (new table in database.py, to be requested from Role 1).
