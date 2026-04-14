import sqlite3
from contextlib import contextmanager
from typing import List, Tuple, Any

# Connection pooling
_connection_pool = []
MAX_CONNECTIONS = 5

@contextmanager
def get_connection():
    """Context manager for efficient connection handling"""
    try:
        if _connection_pool:
            conn = _connection_pool.pop()
        else:
            conn = sqlite3.connect("data.db")
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        yield conn
    finally:
        if len(_connection_pool) < MAX_CONNECTIONS:
            _connection_pool.append(conn)


def create_tables():
    """Create database tables with indexes for better query performance"""
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
        """)

        # Create indexes for frequently queried columns
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(date)")

        conn.commit()


def insert_dummy_data():
    """Insert dummy data with error handling and batch optimization"""
    with get_connection() as conn:
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

        try:
            cursor.executemany("INSERT OR IGNORE INTO customers VALUES (?, ?)", customers)
            cursor.executemany("INSERT OR IGNORE INTO orders VALUES (?, ?, ?, ?)", orders)
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Database insert error: {e}")


def run_query(query: str) -> List[Any]:
    """Execute a query with error handling and validation"""
    # Validate query to prevent accidental harmful commands
    dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER"]
    if any(keyword in query.upper() for keyword in dangerous_keywords):
        raise ValueError("Query contains potentially dangerous operations")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    except sqlite3.Error as e:
        print(f"Query execution error: {e}")
        return []