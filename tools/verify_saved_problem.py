"""
Verify the saved problem in gym_practice_detail
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
import json

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def verify_problem():
    """Verify the most recently saved problem"""

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    cursor = conn.cursor()

    # Query the most recent P1 problem
    cursor.execute("""
        SELECT id, practice_id, detail_title, detail_type, create_date, use_yn, display_order, is_active
        FROM gym_practice_detail
        WHERE detail_type = 'PROBLEM'
        ORDER BY create_date DESC
        LIMIT 3;
    """)

    problems = cursor.fetchall()

    print("\n" + "="*80)
    print("  Most Recent Problems in gym_practice_detail")
    print("="*80)

    if problems:
        for row in problems:
            problem_id, practice_id, title, dtype, create_date, use_yn, display_order, is_active = row
            print(f"\nID: {problem_id}")
            print(f"Practice ID: {practice_id}")
            print(f"Title: {title}")
            print(f"Type: {dtype}")
            print(f"Created: {create_date}")
            print(f"Active: {is_active}, Use YN: {use_yn}, Display Order: {display_order}")
            print("-" * 80)
    else:
        print("  (No records found)")

    # Get the full content_data of the most recent one
    cursor.execute("""
        SELECT id, content_data
        FROM gym_practice_detail
        WHERE detail_type = 'PROBLEM'
        ORDER BY create_date DESC
        LIMIT 1;
    """)

    result = cursor.fetchone()
    if result:
        problem_id, content_data = result
        print(f"\n\nFull Content Data for {problem_id}:")
        print("="*80)
        print(json.dumps(content_data, indent=2, ensure_ascii=False))

    cursor.close()
    conn.close()


if __name__ == "__main__":
    try:
        verify_problem()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
