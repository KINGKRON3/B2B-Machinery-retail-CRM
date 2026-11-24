# B2B-Machinery-retail-CRM

Lightweight B2B CRM web application built with Python, Streamlit, and SQLite for managing heavy machinery sales, inventory, service logs, customer pipelines, and quote/contract documents.

## Local Setup
1. Clone the repository:
   `git clone https://github.com/KINGKRON3/B2B-Machinery-retail-CRM.git`
2. Navigate to the folder:
   `cd B2B-Machinery-retail-CRM`
3. Install dependencies:
   `pip install -r requirements.txt`
4. Run the application:
   `python -m streamlit run app.py`

## Team Roles (Strict File Ownership)
- **Role 1 (Architect & Customers – Arttu):** `database.py`, `app.py`, `pages/2_Customers.py`, `AI_INSTRUCTIONS.md`, `requirements.txt`
- **Role 2 (Sales Pipeline – Casper):** `pages/3_Pipeline.py`
- **Role 3 (Machinery & Inventory – Hugo):** `pages/4_Machinery.py`
- **Role 4 (Analytics & Test Data – Salla):** `pages/1_Dashboard.py`, `seed_data.py`
- **Role 5 (Service & Maintenance – Daniel):** `pages/5_Service.py`
- **Role 6 (Documents & Documentation – Nicolas):** `pages/6_Documents.py`, `README.md`

## Vibe Coding Workflow
1. Edit **only** your assigned file(s) to avoid GitHub merge conflicts.
2. Paste `AI_INSTRUCTIONS.md` into your AI chat and state your role (1–6) before asking for code.
3. Work on your own branch (`git checkout -b feature/your-name`) and push your changes to GitHub.