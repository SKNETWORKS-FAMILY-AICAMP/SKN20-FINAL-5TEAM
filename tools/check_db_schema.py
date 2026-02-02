"""
DB 스키마 확인 스크립트
gym_practice_detail 테이블의 컬럼 정보 조회
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2

# .env 로드
load_dotenv()

# 상위 디렉토리를 path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_schema():
    """gym_practice_detail 테이블 스키마 확인"""

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    cursor = conn.cursor()

    # 테이블 스키마 조회
    cursor.execute("""
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = 'gym_practice_detail'
        ORDER BY ordinal_position;
    """)

    columns = cursor.fetchall()

    print("\n" + "="*80)
    print("  gym_practice_detail 테이블 스키마")
    print("="*80)
    print(f"{'컬럼명':<30} {'타입':<20} {'NULL 허용':<12} {'기본값'}")
    print("-"*80)

    not_null_columns = []

    for col in columns:
        col_name, data_type, is_nullable, default = col
        nullable_str = "YES" if is_nullable == "YES" else "NO (필수)"
        default_str = str(default) if default else "-"

        print(f"{col_name:<30} {data_type:<20} {nullable_str:<12} {default_str}")

        if is_nullable == "NO":
            not_null_columns.append(col_name)

    print("\n" + "="*80)
    print("  필수 컬럼 (NOT NULL):")
    print("="*80)
    for col in not_null_columns:
        print(f"  - {col}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    try:
        check_schema()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
