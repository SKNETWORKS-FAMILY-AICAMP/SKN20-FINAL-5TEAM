"""
Check character varying column lengths in gym_practice_detail
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_lengths():
    """Check character varying column lengths"""

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    cursor = conn.cursor()

    # Query to get character varying columns with their max lengths
    cursor.execute("""
        SELECT
            column_name,
            data_type,
            character_maximum_length,
            is_nullable
        FROM information_schema.columns
        WHERE table_name = 'gym_practice_detail'
          AND data_type = 'character varying'
        ORDER BY column_name;
    """)

    columns = cursor.fetchall()

    print("\n" + "="*80)
    print("  gym_practice_detail VARCHAR Columns")
    print("="*80)
    print(f"{'Column Name':<30} {'Max Length':<15} {'Nullable'}")
    print("-"*80)

    for col in columns:
        col_name, data_type, max_length, is_nullable = col
        nullable_str = "YES" if is_nullable == "YES" else "NO"
        length_str = str(max_length) if max_length else "unlimited"

        print(f"{col_name:<30} {length_str:<15} {nullable_str}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    try:
        check_lengths()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
