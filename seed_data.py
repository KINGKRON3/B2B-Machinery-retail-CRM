from database import get_connection, init_db

def seed():
    init_db()
    conn = get_connection()
    c = conn.cursor()

    # Check if data already exists
    c.execute("SELECT COUNT(*) FROM customers")
    if c.fetchone()[0] > 0:
        conn.close()
        return

    # Sample B2B Customers
    customers = [
        ("Nordic Earthworks Oy", "Pekka Virtanen", "pekka@nordicearthworks.fi", "+358 40 123 4567", "Earthmoving & Excavation"),
        ("Alpine Forestry & Timber GmbH", "Lukas Weber", "l.weber@alpineforestry.de", "+49 170 987 6543", "Forestry"),
        ("Granite Quarry & Mining AB", "Johan Lindqvist", "johan@granitemining.se", "+46 70 555 6677", "Mining & Quarrying"),
        ("Metro Infrastructure Contractors", "Laura Korhonen", "laura@metroinfra.fi", "+358 40 888 9900", "Civil Engineering")
    ]
    c.executemany("INSERT INTO customers (company_name, contact_person, email, phone, industry) VALUES (?, ?, ?, ?, ?)", customers)

    # Sample Heavy Machinery
    machines = [
        ("Caterpillar 320 Excavator", "CAT-320-8841", 1450, 165000.0, "In Stock", None),
        ("Komatsu PC210LC-11 Excavator", "KOM-210-4412", 3200, 128000.0, "Reserved", 1),
        ("Volvo L90H Wheel Loader", "VOL-L90-9920", 850, 189000.0, "In Stock", None),
        ("John Deere 1270G Harvester", "JD-1270-3310", 4100, 295000.0, "Sold", 2),
        ("Sandvik DX800 Surface Drill Rig", "SAN-800-1102", 2900, 340000.0, "In Stock", None)
    ]
    c.executemany("INSERT INTO machines (model_name, serial_number, operating_hours, price, status, customer_id) VALUES (?, ?, ?, ?, ?, ?)", machines)

    # Sample Deals
    deals = [
        ("Komatsu PC210 + Bucket Attachment Package", 1, 2, 134000.0, "Negotiation"),
        ("Harvester Delivery & 2-Year Service Contract", 2, 4, 310000.0, "Won"),
        ("Quote: Volvo L90H for Winter Operations", 4, 3, 189000.0, "Quote"),
        ("New Surface Drill Rig Inquiry", 3, 5, 340000.0, "Lead")
    ]
    c.executemany("INSERT INTO deals (title, customer_id, machine_id, value, stage) VALUES (?, ?, ?, ?, ?)", deals)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed()
    print("Sample data seeded successfully!")
