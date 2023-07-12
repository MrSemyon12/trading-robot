import os
import sqlite3

DB_PATH = os.path.abspath(os.path.join(__file__, "../../app/stats.db"))


def get_orders():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders")
        return cursor.fetchall()


if __name__ == "__main__":
    orders = get_orders()
    for order in orders:
        print(order)
