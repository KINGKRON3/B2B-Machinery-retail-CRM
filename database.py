import sqlite3

DB_NAME = "crm.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables (3 core + service_logs) and load demo data if the database is empty."""
    conn = get_connection()
    c = conn.cursor()

    # 1. Customers (B2B contracting companies & contacts)
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        contact_person TEXT,
        email TEXT,
        phone TEXT,
        industry TEXT
    )''')

    # 2. Machines (Heavy equipment & inventory)
    c.execute('''CREATE TABLE IF NOT EXISTS machines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT NOT NULL,
        serial_number TEXT UNIQUE,
        operating_hours INTEGER,
        price REAL,
        status TEXT DEFAULT 'In Stock', -- In Stock, Reserved, Sold
        customer_id INTEGER,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )''')

    # 3. Deals (Sales pipeline & quotes)
    c.execute('''CREATE TABLE IF NOT EXISTS deals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        customer_id INTEGER,
        machine_id INTEGER,
        value REAL,
        stage TEXT DEFAULT 'Lead', -- Lead, Quote, Negotiation, Won, Lost
        FOREIGN KEY (customer_id) REFERENCES customers (id),
        FOREIGN KEY (machine_id) REFERENCES machines (id)
    )''')

    # 4. Service logs (maintenance, repairs & warranty work per machine)
    c.execute('''CREATE TABLE IF NOT EXISTS service_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        machine_id INTEGER NOT NULL,
        service_date TEXT,
        service_type TEXT,
        description TEXT,
        cost REAL,
        status TEXT DEFAULT 'Scheduled', -- Scheduled, Completed
        FOREIGN KEY (machine_id) REFERENCES machines (id)
    )''')

    # Older databases may have a service_logs table without service_type: add it
    existing = [row[1] for row in c.execute("PRAGMA table_info(service_logs)")]
    if "service_type" not in existing:
        c.execute("ALTER TABLE service_logs ADD COLUMN service_type TEXT")

    conn.commit()
    conn.close()

    # Fill an empty database with realistic demo data
    load_demo_data()


# ---------------------------------------------------------------------------
# Demo data (ids are assigned 1..N in insertion order, so the foreign keys
# below refer to the position of the row in the list above them)
# ---------------------------------------------------------------------------
DEMO_CUSTOMERS = [
    ("Nordic Earthworks Oy", "Pekka Virtanen", "pekka@nordicearthworks.fi", "+358 40 123 4567", "Earthmoving & Excavation"),
    ("Alpine Forestry & Timber GmbH", "Lukas Weber", "l.weber@alpineforestry.de", "+49 170 987 6543", "Forestry"),
    ("Granite Quarry & Mining AB", "Johan Lindqvist", "johan@granitemining.se", "+46 70 555 6677", "Mining & Quarrying"),
    ("Metro Infrastructure Contractors", "Laura Korhonen", "laura@metroinfra.fi", "+358 40 888 9900", "Civil Engineering"),
    ("Baltic Port & Logistics Ltd", "Mari Tamm", "mari.tamm@balticport.ee", "+372 5555 1212", "Port & Logistics"),
    ("Highland Aggregates Ltd", "Callum Reid", "callum.reid@highlandagg.co.uk", "+44 7700 900123", "Aggregates & Recycling"),
]

# (model_name, serial_number, operating_hours, price, status, customer_id)
DEMO_MACHINES = [
    ("Caterpillar 320 Excavator", "CAT-320-8841", 1450, 165000.0, "In Stock", None),
    ("Komatsu PC210LC-11 Excavator", "KOM-210-4412", 3200, 128000.0, "Reserved", 1),
    ("Volvo L90H Wheel Loader", "VOL-L90-9920", 850, 189000.0, "In Stock", None),
    ("John Deere 1270G Harvester", "JD-1270-3310", 4100, 295000.0, "Sold", 2),
    ("Sandvik DX800 Surface Drill Rig", "SAN-800-1102", 2900, 340000.0, "In Stock", None),
    ("Liebherr LH 60 M Material Handler", "LIE-LH60-2207", 5200, 210000.0, "Sold", 5),
    ("Hitachi ZX350LC-7 Excavator", "HIT-350-6015", 2100, 175000.0, "Reserved", 6),
    ("Caterpillar D6 Dozer", "CAT-D6-3374", 1750, 232000.0, "In Stock", None),
]

# (title, customer_id, machine_id, value, stage)
DEMO_DEALS = [
    ("Komatsu PC210 + Bucket Attachment Package", 1, 2, 134000.0, "Negotiation"),
    ("Harvester Delivery & 2-Year Service Contract", 2, 4, 310000.0, "Won"),
    ("Quote: Volvo L90H for Winter Operations", 4, 3, 189000.0, "Quote"),
    ("New Surface Drill Rig Inquiry", 3, 5, 340000.0, "Lead"),
    ("Liebherr Material Handler - Port Fleet Upgrade", 5, 6, 218000.0, "Won"),
    ("Hitachi ZX350LC + Hydraulic Breaker", 6, 7, 182000.0, "Negotiation"),
    ("Cat D6 Dozer for Quarry Haul Road", 3, 8, 240000.0, "Lost"),
]

# (machine_id, service_date, service_type, description, cost, status)
DEMO_SERVICE_LOGS = [
    (4, "2026-09-15", "Warranty Inspection", "Annual harvester head inspection, no faults found", 850.0, "Completed"),
    (2, "2026-10-20", "Hydraulic Repair", "Replaced boom cylinder seals and hydraulic hoses", 3200.0, "Completed"),
    (6, "2026-11-05", "Scheduled Maintenance", "500h service: engine oil, filters and greasing", 1450.0, "Completed"),
    (1, "2026-12-02", "Pre-Delivery Inspection", "Pre-sale check of tracks and undercarriage", 600.0, "Scheduled"),
]


def load_demo_data(force=False):
    """Insert demo customers, machines, deals and service logs.

    force=False: only runs when the customers table is empty.
    force=True:  wipes customers, machines, deals and service logs first (used by the
                 'Reset Demo Data' button). Returns True if data was loaded.
    """
    conn = get_connection()
    try:
        c = conn.cursor()
        if not force and c.execute("SELECT COUNT(*) FROM customers").fetchone()[0] > 0:
            return False

        # Start from a clean slate so the ids below line up with the foreign keys
        c.execute("DELETE FROM service_logs")
        c.execute("DELETE FROM deals")
        c.execute("DELETE FROM machines")
        c.execute("DELETE FROM customers")
        c.execute(
            "DELETE FROM sqlite_sequence "
            "WHERE name IN ('customers', 'machines', 'deals', 'service_logs')"
        )

        c.executemany(
            "INSERT INTO customers (company_name, contact_person, email, phone, industry) "
            "VALUES (?, ?, ?, ?, ?)",
            DEMO_CUSTOMERS,
        )
        c.executemany(
            "INSERT INTO machines (model_name, serial_number, operating_hours, price, status, customer_id) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            DEMO_MACHINES,
        )
        c.executemany(
            "INSERT INTO deals (title, customer_id, machine_id, value, stage) "
            "VALUES (?, ?, ?, ?, ?)",
            DEMO_DEALS,
        )
        c.executemany(
            "INSERT INTO service_logs (machine_id, service_date, service_type, description, cost, status) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            DEMO_SERVICE_LOGS,
        )
        conn.commit()
        return True
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
