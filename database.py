import sqlite3

DB_NAME = "crm.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
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
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
