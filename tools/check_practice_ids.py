"""
Check available practice_ids in gym_practice table
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_practice_ids():
    """Check available practice IDs"""

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    cursor = conn.cursor()

    # First check schema
    print("\n" + "="*80)
    print("  gym_practice Table Schema")
    print("="*80)
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'gym_practice'
        ORDER BY ordinal_position;
    """)
    columns = cursor.fetchall()
    for col_name, col_type in columns:
        print(f"  {col_name}: {col_type}")

    # Query gym_practice table (select all columns with *)
    print("\n" + "="*80)
    print("  gym_practice Table Records")
    print("="*80)
    cursor.execute("""
        SELECT *
        FROM gym_practice
        ORDER BY id;
    """)

    practices = cursor.fetchall()

    if practices:
        print(f"Found {len(practices)} records:")
        for row in practices:
            print(f"  {row}")
    else:
        print("  (No records found)")

    print("\n")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    try:
        check_practice_ids()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
