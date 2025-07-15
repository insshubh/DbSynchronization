import os
import psycopg2
from crate import client as crate_client
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# ----------------------
# Load environment
# ----------------------
load_dotenv()
passwordDB = os.getenv("DB_PASSWORD")

# ----------------------
# Configuration
# ----------------------
POSTGRES_CONFIG = {
    "dbname": "test",
    "user": "postgres",
    "password": passwordDB,
    "host": "localhost",
    "port": 5433
}

CRATEDB_URL = "http://localhost:4200"
SYNC_TABLES = ['products']
SYNC_FILE = r"C:\Users\inssh\Py\Assignment_gravity\Data\last_sync_time.txt"


# ----------------------
# Utility: Sync Time
# ----------------------
def load_last_sync_time():
    if not os.path.exists(SYNC_FILE):
        return datetime(2000, 1, 1, tzinfo=pytz.UTC)
    with open(SYNC_FILE, 'r') as f:
        return datetime.fromisoformat(f.read().strip()).astimezone(pytz.UTC)

def update_last_sync_time():
    with open(SYNC_FILE, 'w') as f:
        f.write(datetime.now(tz=pytz.UTC).isoformat())

# ----------------------
# Connect
# ----------------------

pg_conn = psycopg2.connect(**POSTGRES_CONFIG)
pg_cursor = pg_conn.cursor()

crate_conn = crate_client.connect(CRATEDB_URL, username="crate")
crate_cursor = crate_conn.cursor()

# ----------------------
# Sync Logic
# ----------------------

sync_stats = {}

def sync_table(table_name):
    print(f"\n🔄 Syncing latest row from '{table_name}'...")

    # Fetch most recently updated row
    pg_cursor.execute(
        f"""
        SELECT * FROM {table_name}
        WHERE updated_at = (
            SELECT MAX(updated_at) FROM {table_name}
        )
        """
    )
    rows = pg_cursor.fetchall()
    columns = [desc[0] for desc in pg_cursor.description]

    inserted, deleted, failed = 0, 0, 0

    for row in rows:
        data = dict(zip(columns, row))
        row_id = data['id']

        if data.get("is_deleted"):
            try:
                crate_cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (row_id,))
                deleted += 1
                continue
            except Exception as e:
                print(f"❌ Delete failed for ID {row_id}: {e}")
                failed += 1
                continue

        if "is_deleted" in data:
            del data["is_deleted"]

        keys = list(data.keys())
        values = list(data.values())
        placeholders = ", ".join(["?"] * len(values))
        columns_sql = ", ".join(keys)
        update_sql = ", ".join([f"{col} = EXCLUDED.{col}" for col in keys if col != 'id'])

        query = f"""
            INSERT INTO {table_name} ({columns_sql})
            VALUES ({placeholders})
            ON CONFLICT (id) DO UPDATE SET {update_sql}
        """
        try:
            crate_cursor.execute(query, values)
            inserted += 1
        except Exception as e:
            print(f"❌ Upsert failed for ID {row_id}: {e}")
            failed += 1

    sync_stats[table_name] = {
        'Inserted/Updated': inserted,
        'Deleted': deleted,
        'Failed': failed
    }

def alter_tables_for_tracking(crate_cursor, tables):
    for table in tables:
        for column, col_type in [
            ("updated_at", "TIMESTAMP WITH TIME ZONE"),
            ("is_deleted", "BOOLEAN")
        ]:
            try:
                crate_cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
                print(f"✅ Added column '{column}' to '{table}'")
            except Exception as e:
                if "already has a column" in str(e):
                    print(f"ℹ️ Column '{column}' already exists in '{table}' — skipping.")
                else:
                    print(f"❌ Error adding column '{column}' to '{table}': {e}")  

# ----------------------
# Run Sync
# ----------------------

if __name__ == "__main__":
    # Alter CrateDB tables to ensure required columns exist
    alter_tables_for_tracking(crate_cursor, SYNC_TABLES)
    last_sync_time = load_last_sync_time()

    for table in SYNC_TABLES:
        try:
            sync_table(table)
        except Exception as e:
            print(f"❌ Error syncing {table}: {e}")

    update_last_sync_time()
    print("\n✅ Sync complete. Summary:\n")

    for t, stats in sync_stats.items():
        print(f"📊 {t}: {stats}")

    # Visualize Sync Stats
    fig, ax = plt.subplots(figsize=(12, 6))
    labels = sync_stats.keys()
    inserted = [v['Inserted/Updated'] for v in sync_stats.values()]
    deleted = [v['Deleted'] for v in sync_stats.values()]
    failed = [v['Failed'] for v in sync_stats.values()]

    x = range(len(labels))
    ax.bar(x, inserted, label="Inserted/Updated", color='green')
    ax.bar(x, deleted, bottom=inserted, label="Deleted", color='red')
    ax.bar(x, failed, bottom=[i + d for i, d in zip(inserted, deleted)], label="Failed", color='orange')

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Rows")
    ax.set_title("CrateDB Sync Summary")
    ax.legend()
    ax.grid(True, axis='y')
    plt.tight_layout()
    plt.show()

    pg_cursor.close()
    pg_conn.close()
    crate_conn.close()