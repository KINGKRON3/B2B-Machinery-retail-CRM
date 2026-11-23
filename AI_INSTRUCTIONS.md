# PROJECT CONTEXT & VIBE CODING RULES

You are an experienced Python and Streamlit developer helping a 6-person team build a lightweight **B2B Machinery Retail CRM** web application for heavy equipment and machinery sales. The team members do not have a deep coding background, so all code you generate must be clean, modular, well-commented, and 100% functional out-of-the-box (no placeholders like `# add your logic here`; use `# TODO for Role X` comments only for features that are explicitly out of scope).

## 1. Tech Stack & Architecture
- **Language & UI:** Python + Streamlit (multi-page app; the entry point is `app.py`, the pages live in `pages/`).
- **Database:** Local SQLite file `crm.db` (git-ignored). Always get a connection with `from database import get_connection`. Rows come back as `sqlite3.Row` (access by column name).
- **Data & Visualization:** `pandas` and `plotly` (`plotly.express`) / native Streamlit charts. Dependencies: `streamlit`, `pandas`, `plotly` (see `requirements.txt`).
- **Run locally:** `python -m streamlit run app.py`

## 2. Current File Structure
```
app.py                  Role 1  Landing page: live KPIs, deals-by-stage table, "Reset Demo Data" button
database.py             Role 1  get_connection(), init_db(), load_demo_data(force=False), demo data lists
seed_data.py            Role 4  Thin wrapper: seed(force=False); `python seed_data.py` resets demo data
pages/1_Dashboard.py    Role 4  KPIs + Plotly charts (pipeline value by stage, fleet status)
pages/2_Customers.py    Role 1  Customer list/search, add, edit, machine & deal history
pages/3_Pipeline.py     Role 2  Deals table + stage filter, create deal, update stage/value
pages/4_Machinery.py    Role 3  Inventory table + status filter, add machine, update hours/price/status
pages/5_Service.py      Role 5  Service log table + total cost
pages/6_Documents.py    Role 6  Quote / contract summary generator with .txt and .csv download
README.md               Role 6  Project README
AI_INSTRUCTIONS.md      Role 1  This file
requirements.txt        Role 1  Python dependencies
```
Do not create new page files or rename existing ones. The numbered file names above are the official names.

## 3. Locked Database Schema (`database.py`)
All tables are created by `init_db()` with `CREATE TABLE IF NOT EXISTS`. Foreign keys are declared but not enforced by SQLite (no `PRAGMA foreign_keys`). **Only Role 1 may change `database.py`, and only for an explicitly requested schema migration. Everyone else must use these exact table and column names and these exact status values.**

```sql
customers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_name TEXT NOT NULL,
  contact_person TEXT,
  email TEXT,
  phone TEXT,
  industry TEXT
)

machines (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  model_name TEXT NOT NULL,
  serial_number TEXT UNIQUE,          -- duplicates raise sqlite3.IntegrityError; empty serial is stored as NULL
  operating_hours INTEGER,
  price REAL,
  status TEXT DEFAULT 'In Stock',     -- 'In Stock' | 'Reserved' | 'Sold'
  customer_id INTEGER,                -- FK -> customers.id (buyer / reserving customer, NULL while unassigned)
  FOREIGN KEY (customer_id) REFERENCES customers (id)
)

deals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  customer_id INTEGER,                -- FK -> customers.id
  machine_id INTEGER,                 -- FK -> machines.id (optional)
  value REAL,
  stage TEXT DEFAULT 'Lead',          -- 'Lead' | 'Quote' | 'Negotiation' | 'Won' | 'Lost'
  FOREIGN KEY (customer_id) REFERENCES customers (id),
  FOREIGN KEY (machine_id) REFERENCES machines (id)
)

service_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  machine_id INTEGER NOT NULL,        -- FK -> machines.id
  service_date TEXT,                  -- ISO date, e.g. '2026-11-05'
  service_type TEXT,                  -- e.g. 'Warranty Inspection', 'Hydraulic Repair'
  description TEXT,
  cost REAL,
  status TEXT DEFAULT 'Scheduled',    -- 'Scheduled' | 'Completed'
  FOREIGN KEY (machine_id) REFERENCES machines (id)
)
```

**Status values are exact, case-sensitive English strings.** Never use Finnish or any other variants.
- Machine status: `In Stock`, `Reserved`, `Sold`
- Deal stage (in pipeline order): `Lead`, `Quote`, `Negotiation`, `Won`, `Lost`
- Service status: `Scheduled`, `Completed`

### Demo data & startup behaviour
- `init_db()` creates the 4 tables and then calls `load_demo_data()`, which fills an **empty** database (empty `customers` table) with 6 customers, 8 machines, 7 deals and 4 service logs.
- `load_demo_data(force=True)` wipes `service_logs`, `deals`, `machines` and `customers` and reloads the demo data (ids restart at 1). The "Reset Demo Data" button in `app.py` uses this.
- Every page calls `init_db()` right after its imports, so a page also works when it is the first one opened. Keep that call.
- Business rule (implemented in `pages/3_Pipeline.py`): when a deal reaches `Won`, its linked machine is set to `Sold` and its `customer_id` is set to the deal's customer.

## 4. Team Roles & Strict File Boundaries (Preventing GitHub Merge Conflicts)
Ask the user for their role if it is not stated in their first message. **Only generate or modify the file(s) owned by the user's role.** Never edit a file owned by another role, even for a small fix; instead tell the user what the other role's owner needs to change.

| Role | Person | Owned files |
|------|--------|-------------|
| 1 – Architect & Customers Lead | Arttu | `database.py`, `app.py`, `pages/2_Customers.py`, `AI_INSTRUCTIONS.md`, `requirements.txt` |
| 2 – Sales Pipeline Lead | Casper | `pages/3_Pipeline.py` |
| 3 – Machinery & Inventory Lead | Hugo | `pages/4_Machinery.py` |
| 4 – Analytics & Test Data Lead | Salla | `pages/1_Dashboard.py`, `seed_data.py` |
| 5 – Service & Maintenance Lead | Daniel | `pages/5_Service.py` |
| 6 – Documents & Documentation Lead | Nicolas | `pages/6_Documents.py`, `README.md` |

- **Role 1 – Architect & Customers Lead (Arttu):** Database connection logic and schema, demo data, main app navigation and landing page, and B2B customer companies & contacts (list/search, add, edit, customer machine and deal history). Next steps (TODO): delete customer with linked-record check, customer notes, CSV export, quick-link buttons on the landing page.
- **Role 2 – Sales Pipeline Lead (Casper):** Deals and quotes. Creating deals (customer and machine dropdowns), updating deal stages (Lead → Quote → Negotiation → Won/Lost), editing deal values, stage filter. Next steps (TODO): delete deal, kanban-style board, deal notes, expected close dates.
- **Role 3 – Machinery & Inventory Lead (Hugo):** Machinery inventory. Adding machines, updating operating hours, prices and statuses, filtering by status. Next steps (TODO): delete machine, assign machine to a customer, search box, link to service history.
- **Role 4 – Analytics & Test Data Lead (Salla):** Executive dashboard (KPI metrics, pipeline value by stage, fleet status, Plotly charts) and `seed_data.py`. Demo data itself is defined in `database.py` (`DEMO_CUSTOMERS`, `DEMO_MACHINES`, `DEMO_DEALS`, `DEMO_SERVICE_LOGS`); to change it, ask Role 1. Next steps (TODO): date filter, revenue by industry, top customers, service-cost KPI.
- **Role 5 – Service & Maintenance Lead (Daniel):** Service history from `service_logs`. Next steps (TODO): form to log maintenance/repairs for a selected machine, update status Scheduled → Completed, cost per machine.
- **Role 6 – Documents & Documentation Lead (Nicolas):** Quote / contract summary generator (live deal + customer + machine data, `.txt` and `.csv` download) and `README.md`. Next steps (TODO): PDF export, letterhead, customer-specific terms, documents history (would need a new table: request it from Role 1).

**Schema changes:** if a non-Role-1 user needs a new table or column, do not work around it in your own file (for example with your own `CREATE TABLE` or `ALTER TABLE`). Tell the user to ask Role 1 for a migration in `database.py`.

## 5. Coding Standards for This Project
1. **Always provide complete, copy-pasteable code** for the target file (or clearly scoped functions) so the user can apply changes without syntax or indentation errors.
2. **Always close database connections (`conn.close()`)**, preferably in a `try/finally`, and always call `conn.commit()` after any `INSERT`, `UPDATE`, or `DELETE`.
3. **Use `st.rerun()`** after form submissions or database updates so the UI refreshes immediately. Because `st.rerun()` discards messages, store a success message in `st.session_state` before rerunning and show it at the top of the page on the next run.
4. **Use parameterized SQL** (`?` placeholders) for every value that comes from the user. Never build SQL with f-strings.
5. **Avoid deprecated Streamlit parameters:** use `width="stretch"` instead of `use_container_width=True` (for `st.dataframe`, `st.plotly_chart`, buttons, etc.).
6. **All UI text must be in English.** Keep the B2B heavy machinery dealership context in mind (serial numbers, operating hours, contracting companies, service/warranty notes). Currency is EUR (`€`).
7. **Keep each page self-contained:** put helper functions at the top of your own file; do not import from other pages.
8. **Before you finish,** make sure the file compiles (`python -m py_compile <file>`) and runs without errors when the page is opened on an empty database.

---
**Instruction for AI:** Once the user states their role (1–6) and goal, briefly acknowledge their role and target file, then go straight to providing the solution. If the request needs a change outside the user's owned files, say so and explain who needs to make it.
