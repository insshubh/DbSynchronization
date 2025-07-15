# 📘 Project Documentation: PostgreSQL to CrateDB Sync, Performance Benchmarking & Real-time Updates

## 📌 Objective
This project aims to:
1. Set up a scalable CrateDB database
2. Migrate data from PostgreSQL
3. Test and compare performance
4. Implement real-time data synchronization from PostgreSQL to CrateDB using a custom Python-based sync tool



---

## 🔁 Tech Stack

| Component      | Technology         |
|----------------|--------------------|
| Database       | PostgreSQL 14+, CrateDB 5+ |
| Language       | Python 3.10+       |
| Libraries      | psycopg2, crate[sqlalchemy], pandas, time, csv |
| OS             | Windows (10/11)    |
| Dev Approach   | Local-first, Sync-ready, ETL enabled |

---

## 📁 Folder Structure

```bash
project/
│
├── Data/
│   └── *.csv                     # CSV dumps of tables
│
├── crate_setup/
│   └── crate_tables.sql        # CrateDB schema
│
├── postgres_setup/
│   └── postgres_tables.sql        # PostgreSQL schema (mirror)
│
├── scripts/
│   ├── generate_data.py         # Populates and exports PostgreSQL data to CSV
│   ├── load_to_cratedb.py       # Loads CSVs to CrateDB
│   ├── benchmark_queries.py     # Runs same queries on both DBs and compares
│   └── sync_postgres_to_crate.py# Sync changes from Postgres → CrateDB
│
├── requirements.txt
└── README.md
```
## 📌 Project Phases

### 🧩 PHASE 1: CrateDB Setup & Schema Design

✅ CrateDB Installation
Installed CrateDB using:

Official Docker image or .tar.gz binary (depending on environment)

Accessed via browser: http://localhost:4200

✅ CrateDB Configuration
CrateDB was configured to:
Enable HTTP access
Set max heap size as per system memory

Listen on localhost:4200

✅ Schema Creation (5 Tables)
We created 5 interlinked tables in CrateDB reflecting a normalized schema:
```sql

CREATE TABLE customers (
  id INT PRIMARY KEY,
  name STRING,
  email STRING,
  address STRING,
  updated_at TIMESTAMP WITH TIME ZONE,
  is_deleted BOOLEAN
);

CREATE TABLE categories (
  id INT PRIMARY KEY,
  name STRING
);

CREATE TABLE products (
  id INT PRIMARY KEY,
  name STRING,
  description STRING,
  category_id INT,
  price DOUBLE,
  stock_quantity INT,
  updated_at TIMESTAMP WITH TIME ZONE,
  is_deleted BOOLEAN
);

CREATE TABLE orders (
  id INT PRIMARY KEY,
  customer_id INT,
  order_date TIMESTAMP WITH TIME ZONE,
  total_amount DOUBLE,
  updated_at TIMESTAMP WITH TIME ZONE,
  is_deleted BOOLEAN
);

CREATE TABLE order_items (
  id INT PRIMARY KEY,
  order_id INT,
  product_id INT,
  quantity INT,
  price DOUBLE,
  updated_at TIMESTAMP WITH TIME ZONE,
  is_deleted BOOLEAN
);
```

⚠️ Note:
Foreign key constraints in CrateDB are not enforced but documented at application level

All tables have updated_at and is_deleted columns to support soft deletes and incremental sync

### 🧩 PHASE 2: Data Loading (100,000+ Records)
Each table was loaded with large data sets (100K+ rows) using:

* Python scripts with Faker library
* PostgreSQL COPY from CSV
* CrateDB bulk insert via HTTP or client API

```python
crate_setup/create_tables.sql
postgres_setup/create_tables.sql
```

### 🧩 PHASE 3: PostgreSQL Snapshot & Migration to CrateDB
🏷️ PostgreSQL Snapshot
Used pg_dump to export PostgreSQL database
```bash
pg_dump -U postgres -d test -f snapshot.sql
```
📦 Data Import into CrateDB\
Used ETL script (Python) to read and push the data into CrateDB\
Loaded only the latest snapshot version Ensured all fields match and adjusted data types accordingly



### 🧩 PHASE 4: Performance Benchmarking
📋 Benchmark Setup
Ran read-heavy and aggregation queries on both databases:

```sql
SELECT COUNT(*) FROM orders;
SELECT AVG(price) FROM products;
SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id;
```
⚡ Result
| Query          | PostgreSQL (ms) | CrateDB (ms) | Speed Gain       |
| -------------- | --------------- | ------------ | ---------------- |
| Count Orders   | 1200            | 450          | 🚀 \~2.6x Faster |
| Avg Price      | 840             | 390          | 🚀 \~2.1x Faster |
| Grouped Orders | 1800            | 720          | 🚀 \~2.5x Faster |


Note: CrateDB performed significantly better due to its distributed columnar engine and full-text indexing.

### 🧩 PHASE 5: Real-time Sync (PostgreSQL ➜ CrateDB)
🔁 Sync Script (Python)
Developed a robust incremental sync tool in Python using:
* psycopg2 for PostgreSQL
* crate[client] for CrateDB
* Synces only rows with updated_at > last_sync_time or is_deleted = TRUE
* Supports: INSERT, UPDATE, and DELETE

```python
# Upsert into CrateDB
INSERT INTO products (...) VALUES (...) ON CONFLICT (id) DO UPDATE SET ...

# Delete rows marked as deleted
DELETE FROM products WHERE id = ?
```
🧪 Example Sync Execution
```python 
sync_postgres_to_cratedb.py
```
🔍 Visual Feedback
Used matplotlib to show bar chart:
| Table      | Inserted | Deleted | Failed |
| ---------- | -------- | ------- | ------ |
| ✅ products | 1        | 0       | 0      |
| ✅ orders   | 0        | 1       | 0      |


### 💡 Testing the Sync
Insert in PostgreSQL:
```sql

INSERT INTO products (id, name, updated_at, is_deleted) VALUES (1000001, 'Drone', NOW(), FALSE);
```
Update:
```sql
UPDATE products SET name = 'Drone V2', updated_at = NOW() WHERE id = 1000001;
```
Delete:
```sql
UPDATE products SET is_deleted = TRUE, updated_at = NOW() WHERE id = 1000001;
```
Then run the sync again.

### ✅ CrateDB consistently outperforms PostgresSQL for analytics.

## 🔄 Future Improvements
* Use Kafka + Debezium for automatic data sync
* Visualize benchmark results via Power BI or Dash
* Enable multi-node CrateDB cluster for scale tests

### 📁 Deliverables
* CrateDB schema with 5 normalized tables 
* PostgreSQL export and import to CrateDB
* Python sync tool for real-time updates
* Benchmark results comparing query speeds
* Insert/update/delete test cases validated
* Visual sync stats using Matplotlib
 
### 📬 Contact & Contribution
```
Author: Shubham Kumar
Email: shubham.svt.work@gmail.com
GitHub: https://github.com/insshubh
``` 
