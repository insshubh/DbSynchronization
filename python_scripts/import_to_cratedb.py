from crate import client

tables = ["customers", "categories", "products", "orders", "order_items"]
base_path = "file:///C:/Users/inssh/Py/Assignment_gravity/Data/"

connection = client.connect("http://localhost:4200", username="crate")
cursor = connection.cursor()

for table in tables:
    path = base_path + table + ".csv"
    try:
        print(f"Importing {table}...")
        cursor.execute(f"""
            COPY {table} FROM '{path}' WITH (format='csv', header=true)
        """)
        print(f"✅ {table} imported.")
    except Exception as e:
        print(f"❌ Failed to import {table}: {e}")

connection.close()
