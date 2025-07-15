import random
from datetime import datetime, timedelta
from crate import client
from crate.client.exceptions import ProgrammingError
import time

def random_date():
    end = datetime.now()
    start = end - timedelta(days=3 * 365)
    return start + (end - start) * random.random()

def create_tables(cursor):
    print("Dropping old tables (if exist)...")
    for table in ["order_items", "orders", "products", "categories", "customers"]:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
        except Exception as e:
            print(f"Could not drop {table}: {e}")

    print("Creating new tables...")
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            registration_date TIMESTAMP,
            address OBJECT AS (
                street TEXT,
                city TEXT,
                zip TEXT
            )
        )
    """)
    
    cursor.execute("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            category_id INTEGER,
            price DOUBLE,
            stock_quantity INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date TIMESTAMP,
            status TEXT,
            total_amount DOUBLE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE order_items (
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            unit_price DOUBLE,
            PRIMARY KEY (order_id, product_id)
        )
    """)

def insert_data(cursor):
    print("Inserting customers...")
    for i in range(1, 100001):
        address = {
            'street': f"Street {i % 100 + 1}",
            'city': random.choice(['New York', 'London', 'Berlin', 'Tokyo', 'Paris']),
            'zip': str(10000 + i % 90000)
        }
        try:
            cursor.execute("""
                INSERT INTO customers (id, name, email, registration_date, address) 
                VALUES (?, ?, ?, ?, ?)
            """, (i, f"Customer {i}", f"customer{i}@example.com", random_date(), address))
        except ProgrammingError as e:
            if "DuplicateKeyException" in str(e):
                continue
            raise
    cursor.execute("REFRESH TABLE customers")

    print("Inserting categories...")
    for i in range(1, 100001):
        try:
            cursor.execute("""
                INSERT INTO categories (id, name, description) 
                VALUES (?, ?, ?)
            """, (i, f"Category {i}", f"Description for category {i}"))
        except ProgrammingError as e:
            if "DuplicateKeyException" in str(e):
                continue
            raise
    cursor.execute("REFRESH TABLE categories")

    print("Inserting products...")
    for i in range(1, 100001):
        try:
            cursor.execute("""
                INSERT INTO products (id, name, description, category_id, price, stock_quantity) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                i, f"Product {i}", f"Description for product {i}",
                random.randint(1, 100000),
                round(10 + random.random() * 990, 2),
                random.randint(0, 1000)
            ))
        except ProgrammingError as e:
            if "DuplicateKeyException" in str(e):
                continue
            raise
    cursor.execute("REFRESH TABLE products")

    print("Inserting orders...")
    for i in range(1, 100001):
        try:
            status = random.choices(['completed', 'shipped', 'pending'], weights=[0.7, 0.2, 0.1])[0]
            cursor.execute("""
                INSERT INTO orders (id, customer_id, order_date, status, total_amount) 
                VALUES (?, ?, ?, ?, ?)
            """, (
                i,
                random.randint(1, 100000),
                random_date(),
                status,
                round(100 + random.random() * 900, 2)
            ))
        except ProgrammingError as e:
            if "DuplicateKeyException" in str(e):
                continue
            raise
    cursor.execute("REFRESH TABLE orders")

    print("Inserting order items...")
    item_count = 0
    for order_id in range(1, 100001):
        used_product_ids = set()
        for _ in range(random.randint(1, 5)):
            product_id = random.randint(1, 100000)
            if product_id in used_product_ids:
                continue
            used_product_ids.add(product_id)
            try:
                cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price) 
                    VALUES (?, ?, ?, ?)
                """, (
                    order_id, product_id,
                    random.randint(1, 10),
                    round(10 + random.random() * 990, 2)
                ))
                item_count += 1
            except ProgrammingError as e:
                if "DuplicateKeyException" in str(e):
                    continue
                raise
    cursor.execute("REFRESH TABLE order_items")
    print(f"✅ Inserted {item_count} unique order_items.")

def run_custom_query(cursor, table_name, query):
    """Run a custom SQL query on a given table"""
    print(f"\n🔍 Executing query on table: {table_name}")
    print(f"📄 Query: {query}")
    
    try:
        start = time.time()
        cursor.execute(query)
        results = cursor.fetchall()
        elapsed = time.time() - start

        print(f"✅ Query executed successfully in {elapsed:.4f} seconds.")
        print(f"📊 Returned {len(results)} rows.")
        
        # Print first 5 rows only
        for i, row in enumerate(results[:5]):
            print(f"{i+1}: {row}")

        if len(results) > 5:
            print(f"... and {len(results) - 5} more rows.")

    except Exception as e:
        print(f"❌ Error running query: {e}")



# ------------------------
# Main Execution
# ------------------------

if __name__ == "__main__":
    try:
        connection = client.connect("http://localhost:4200", username="crate")
        cursor = connection.cursor()
        
        create_tables(cursor)
        insert_data(cursor)

        print("🎉 All tables created and data inserted successfully!")

    except Exception as e:
        print(f"❌ Error occurred: {e}")
    finally:
        if 'connection' in locals():
            connection.close()
