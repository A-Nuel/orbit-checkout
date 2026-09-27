#!/usr/bin/env python3
"""Populate the orders database with a few realistic sample rows."""

from datetime import datetime, timedelta
from src.orders.order_store import OrderStore

SAMPLES = [
    {
        "product_name": "Orbit Pro Headphones",
        "amount_cents": 14900,
        "customer_email": "maya.chen@example.com",
        "status": "paid",
        "stripe_charge_id": "ch_3NqK8a2eZvKYlo2C0a1b2c3d",
        "days_ago": 12,
    },
    {
        "product_name": "Orbit Studio Monitors (pair)",
        "amount_cents": 39900,
        "customer_email": "jordan.lee@example.org",
        "status": "paid",
        "stripe_charge_id": "ch_3NpR7b2eZvKYlo2C0e4f5g6h",
        "days_ago": 8,
    },
    {
        "product_name": "Orbit Pro Headphones",
        "amount_cents": 14900,
        "customer_email": "sam.okonkwo@example.net",
        "status": "failed",
        "stripe_charge_id": "ch_3NoM6c2eZvKYlo2C0i7j8k9l",
        "days_ago": 5,
    },
    {
        "product_name": "Orbit Travel Case",
        "amount_cents": 4900,
        "customer_email": "priya.sharma@example.com",
        "status": "paid",
        "stripe_charge_id": "ch_3NnL5d2eZvKYlo2C0m0n1o2p",
        "days_ago": 3,
    },
    {
        "product_name": "Orbit Pro Headphones",
        "amount_cents": 14900,
        "customer_email": "alex.rivera@example.com",
        "status": "pending",
        "stripe_charge_id": None,
        "days_ago": 1,
    },
]


def main():
    store = OrderStore()
    conn = store._get_conn()
    conn.execute("DELETE FROM orders")
    conn.commit()
    conn.close()

    now = datetime.utcnow()
    for sample in SAMPLES:
        created = (now - timedelta(days=sample["days_ago"])).isoformat()
        conn = store._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO orders (product_name, amount_cents, currency, customer_email, status, stripe_charge_id, created_at, updated_at)
            VALUES (?, ?, 'usd', ?, ?, ?, ?, ?)
            """,
            (
                sample["product_name"],
                sample["amount_cents"],
                sample["customer_email"],
                sample["status"],
                sample["stripe_charge_id"],
                created,
                created,
            ),
        )
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        print(f"  seeded order #{order_id}: {sample['product_name']} ({sample['status']})")

    print(f"Done. {len(SAMPLES)} sample orders ready.")


if __name__ == "__main__":
    main()
