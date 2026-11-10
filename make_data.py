import sqlite3, random
from datetime import date, timedelta

random.seed(42)
conn = sqlite3.connect("data/shop.db")
c = conn.cursor()
c.executescript("""
DROP TABLE IF EXISTS orders; DROP TABLE IF EXISTS products; DROP TABLE IF EXISTS customers;
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT, region TEXT);
CREATE TABLE products  (product_id INTEGER PRIMARY KEY, name TEXT, category TEXT, unit_price REAL);
CREATE TABLE orders    (order_id INTEGER PRIMARY KEY, customer_id INT, product_id INT,
                        quantity INT, order_date TEXT, total_price REAL);
""")

regions = ["Baku", "Ganja", "Sumqayit", "Lankaran"]
categories = {"Electronics": (80, 900), "Clothing": (15, 120), "Books": (5, 40),
              "Home": (20, 300), "Sports": (10, 200)}

for i in range(1, 201):
    c.execute("INSERT INTO customers VALUES (?,?,?)", (i, f"Customer {i}", random.choice(regions)))

pid = 1
for cat, (lo, hi) in categories.items():
    for _ in range(8):
        c.execute("INSERT INTO products VALUES (?,?,?,?)",
                  (pid, f"{cat} item {pid}", cat, round(random.uniform(lo, hi), 2)))
        pid += 1

products = c.execute("SELECT product_id, category, unit_price FROM products").fetchall()
d, oid = date(2025, 1, 1), 1
while d <= date(2025, 12, 31):
    for _ in range(random.randint(8, 15)):
        p = random.choice(products)
        # Bilərəkdən qoyulan hadisə: mart ayında Electronics satışı kəskin düşür
        if p[1] == "Electronics" and d.month == 3 and random.random() < 0.6:
            continue
        qty = random.randint(1, 4)
        c.execute("INSERT INTO orders VALUES (?,?,?,?,?,?)",
                  (oid, random.randint(1, 200), p[0], qty, d.isoformat(), round(qty * p[2], 2)))
        oid += 1
    d += timedelta(days=1)

conn.commit(); conn.close()
print("Done")