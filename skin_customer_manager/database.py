import sqlite3

DATABASE_FILE = "skin_shop.db"


def get_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_customers_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            birth TEXT,
            skin_type TEXT,
            memo TEXT,
            created_at TEXT
        )
    """)


def create_visits_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            service TEXT NOT NULL,
            price INTEGER NOT NULL,
            memo TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)


def initialize_database():
    conn = get_connection()
    create_customers_table(conn)
    create_visits_table(conn)
    conn.commit()
    conn.close()


def _row_to_customer(row):
    return {
        "id": str(row["id"]),
        "name": row["name"] or "",
        "phone": row["phone"] or "",
        "birth": row["birth"] or "",
        "skin_type": row["skin_type"] or "",
        "memo": row["memo"] or "",
        "created_at": row["created_at"] or "",
    }


def _row_to_visit(row):
    return {
        "visit_id": str(row["id"]),
        "customer_id": str(row["customer_id"]),
        "date": row["date"] or "",
        "service": row["service"] or "",
        "price": str(row["price"]),
        "memo": row["memo"] or "",
    }


def load_customers():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM customers ORDER BY id"
    ).fetchall()
    conn.close()
    return [_row_to_customer(row) for row in rows]


def get_customer_by_id(customer_id):
    if not str(customer_id).isdigit():
        return None

    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM customers WHERE id = ?",
        (int(customer_id),),
    ).fetchone()
    conn.close()

    if not row:
        return None

    return _row_to_customer(row)


def insert_customer(name, phone, birth, skin_type, memo, created_at):
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO customers (name, phone, birth, skin_type, memo, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (name, phone, birth, skin_type, memo, created_at),
    )
    conn.commit()
    customer_id = cursor.lastrowid
    conn.close()
    return customer_id


def update_customer(customer_id, name, phone, birth, skin_type, memo):
    conn = get_connection()
    conn.execute(
        """
        UPDATE customers
        SET name = ?, phone = ?, birth = ?, skin_type = ?, memo = ?
        WHERE id = ?
        """,
        (name, phone, birth, skin_type, memo, int(customer_id)),
    )
    conn.commit()
    conn.close()


def delete_customer(customer_id):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM customers WHERE id = ?", (int(customer_id),))
        conn.commit()
    finally:
        conn.close()


def load_visits():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM visits ORDER BY id"
    ).fetchall()
    conn.close()
    return [_row_to_visit(row) for row in rows]


def get_visits_by_customer_id(customer_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM visits WHERE customer_id = ? ORDER BY id",
        (int(customer_id),),
    ).fetchall()
    conn.close()
    return [_row_to_visit(row) for row in rows]


def insert_visit(customer_id, date, service, price, memo):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO visits (customer_id, date, service, price, memo)
        VALUES (?, ?, ?, ?, ?)
        """,
        (int(customer_id), date, service, int(price), memo),
    )
    conn.commit()
    conn.close()


def get_visit_by_id(visit_id):
    if not str(visit_id).isdigit():
        return None

    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM visits WHERE id = ?",
        (int(visit_id),),
    ).fetchone()
    conn.close()

    if not row:
        return None

    return _row_to_visit(row)


def update_visit(visit_id, customer_id, date, service, price, memo):
    conn = get_connection()
    conn.execute(
        """
        UPDATE visits
        SET customer_id = ?, date = ?, service = ?, price = ?, memo = ?
        WHERE id = ?
        """,
        (int(customer_id), date, service, int(price), memo, int(visit_id)),
    )
    conn.commit()
    conn.close()


def delete_visit(visit_id):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM visits WHERE id = ?", (int(visit_id),))
        conn.commit()
    finally:
        conn.close()


def search_customers(keyword):
    conn = get_connection()
    pattern = f"%{keyword}%"
    rows = conn.execute(
        """
        SELECT * FROM customers
        WHERE name LIKE ? OR phone LIKE ?
        ORDER BY id
        """,
        (pattern, pattern),
    ).fetchall()
    conn.close()
    return [_row_to_customer(row) for row in rows]


def get_visits_with_customer_by_id(customer_id):
    if not str(customer_id).isdigit():
        return None, []

    conn = get_connection()
    rows = conn.execute(
        """
        SELECT
            visits.id AS visit_id,
            visits.customer_id,
            visits.date,
            visits.service,
            visits.price,
            visits.memo,
            customers.name AS customer_name
        FROM visits
        INNER JOIN customers ON visits.customer_id = customers.id
        WHERE customers.id = ?
        ORDER BY visits.id
        """,
        (int(customer_id),),
    ).fetchall()
    conn.close()

    if not rows:
        customer = get_customer_by_id(customer_id)
        return customer, []

    customer = {
        "id": str(rows[0]["customer_id"]),
        "name": rows[0]["customer_name"] or "",
    }
    visits = [_row_to_visit_join(row) for row in rows]
    return customer, visits


def get_all_visits_with_customer():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT
            visits.id AS visit_id,
            visits.customer_id,
            visits.date,
            visits.service,
            visits.price,
            visits.memo,
            customers.name AS customer_name
        FROM visits
        INNER JOIN customers ON visits.customer_id = customers.id
        ORDER BY visits.id
        """
    ).fetchall()
    conn.close()
    return [_row_to_visit_join(row) for row in rows]


def _row_to_visit_join(row):
    return {
        "visit_id": str(row["visit_id"]),
        "customer_id": str(row["customer_id"]),
        "customer_name": row["customer_name"] or "",
        "date": row["date"] or "",
        "service": row["service"] or "",
        "price": str(row["price"]),
        "memo": row["memo"] or "",
    }


def customer_has_visits(customer_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM visits WHERE customer_id = ? LIMIT 1",
        (int(customer_id),),
    ).fetchone()
    conn.close()
    return row is not None
