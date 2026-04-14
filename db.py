import sqlite3

def get_connection():
    conn = sqlite3.connect("data.db")
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        amount REAL,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()


def insert_dummy_data():
    conn = get_connection()
    cursor = conn.cursor()

    customers = [
        (1, "Ali"),
        (2, "Ahmed"),
        (3, "Sara")
    ]

    orders = [
        (1, 1, 100, "2024-01-01"),
        (2, 1, 200, "2024-01-02"),
        (3, 2, 150, "2024-01-03"),
        (4, 3, 300, "2024-01-04")
    ]

    cursor.executemany("INSERT OR IGNORE INTO customers VALUES (?, ?)", customers)
    cursor.executemany("INSERT OR IGNORE INTO orders VALUES (?, ?, ?, ?)", orders)

    conn.commit()
    conn.close()


def run_query(query):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(query)
    result = cursor.fetchall()

    conn.close()
    return result