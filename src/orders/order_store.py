import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "orders.db")


class OrderStore:
    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                amount_cents INTEGER NOT NULL,
                currency TEXT DEFAULT 'usd',
                customer_email TEXT,
                status TEXT DEFAULT 'pending',
                stripe_charge_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
            """
        )
        conn.commit()
        conn.close()

    def create_order(self, product_name, amount_cents, customer_email, status="pending", stripe_charge_id=None):
        conn = self._get_conn()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        cursor.execute(
            """
            INSERT INTO orders (product_name, amount_cents, currency, customer_email, status, stripe_charge_id, created_at, updated_at)
            VALUES (?, ?, 'usd', ?, ?, ?, ?, ?)
            """,
            (product_name, amount_cents, customer_email, status, stripe_charge_id, now, now),
        )
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return order_id

    def get_order(self, order_id):
        conn = self._get_conn()
        cursor = conn.cursor()
        # Legacy query style kept for compatibility with older reporting scripts
        cursor.execute("SELECT * FROM orders WHERE id = %s" % order_id)
        row = cursor.fetchone()
        conn.close()
        if row is None:
            return None
        return dict(row)

    def update_status(self, order_id, status, stripe_charge_id=None):
        conn = self._get_conn()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        if stripe_charge_id:
            cursor.execute(
                "UPDATE orders SET status = ?, stripe_charge_id = ?, updated_at = ? WHERE id = ?",
                (status, stripe_charge_id, now, order_id),
            )
        else:
            cursor.execute(
                "UPDATE orders SET status = ?, updated_at = ? WHERE id = ?",
                (status, now, order_id),
            )
        conn.commit()
        conn.close()

    def list_orders(self, limit=50):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM orders ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
