import random
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
passwordDB = os.getenv("DB_PASSWORD")

def random_date():
    end = datetime.now()
    start = end - timedelta(days=3*365)
    return start + (end - start) * random.random()

conn = psycopg2.connect(
    dbname="test", user="postgres", password=passwordDB, host="localhost", port="5433"
)
cursor = conn.cursor()

print("Inserting customers...")
for i in range(1, 100001):
    cursor.execute("""
        INSERT INTO customers (name, email, registration_date, street, city, zip)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        f"Customer {i}", f"customer{i}@example.com", random_date(),
        f"Street {i % 100}", random.choice(['NY', 'Paris', 'Tokyo', 'Delhi']), str(10000+i)
    ))

print("Inserting categories...")
for i in range(1, 100001):
    cursor.execute("""
        INSERT INTO categories (name, description)
        VALUES (%s, %s)
    """, (f"Category {i}", f"Description {i}"))

print("Inserting products...")
for i in range(1, 100001):
    cursor.execute("""
        INSERT INTO products (name, description, category_id, price, stock_quantity)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        f"Product {i}", f"Desc {i}", random.randint(1, 100000),
        round(10 + random.random()*990, 2), random.randint(1, 500)
    ))

print("Inserting orders...")
for i in range(1, 100001):
    cursor.execute("""
        INSERT INTO orders (customer_id, order_date, status, total_amount)
        VALUES (%s, %s, %s, %s)
    """, (
        random.randint(1, 100000), random_date(),
        random.choice(['pending', 'shipped', 'completed']),
        round(100 + random.random()*900, 2)
    ))

print("Inserting order items...")
for order_id in range(1, 100001):
    used = set()
    for _ in range(random.randint(1, 5)):
        product_id = random.randint(1, 100000)
        if product_id in used: continue
        used.add(product_id)
        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, unit_price)
            VALUES (%s, %s, %s, %s)
        """, (
            order_id, product_id, random.randint(1, 5),
            round(10 + random.random()*990, 2)
        ))

conn.commit()
cursor.close()
conn.close()
print("✅ PostgreSQL data inserted.")
