"""
Supabase (PostgreSQL) DB 저장
gym_practice_detail 테이블에 문제 저장
"""

import os
import json
import psycopg2
import uuid
from datetime import datetime


def save_problem(problem: dict, practice_id: str = "unit02"):
    """
    Supabase (PostgreSQL)에 문제 저장
    테이블: gym_practice_detail

    Args:
        problem: 생성된 P1 문제 JSON
        practice_id: practice_id (기본값: unit02, 버그헌트/Debug Practice 유닛)

    Raises:
        psycopg2.Error: DB 연결 또는 저장 실패 시
    """

    # DB 연결
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    cursor = conn.cursor()

    try:
        # INSERT
        # 고유 ID 생성 (varchar(20) 제약으로 짧은 ID 사용)
        # 형식: P1_YYYYMMDDHHMMSS (최대 17자)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = f"{problem['id']}_{timestamp}"

        cursor.execute("""
            INSERT INTO gym_practice_detail
            (id, practice_id, detail_title, detail_type, content_data, is_active, create_date, update_date, use_yn, display_order)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            unique_id,       # 고유 ID (예: P1_20260202143022)
            practice_id,     # practice_id (예: unit02)
            problem["project_title"],
            "PROBLEM",
            json.dumps(problem, ensure_ascii=False),  # JSON으로 저장
            True,
            datetime.now(),  # 생성 시각
            datetime.now(),  # 수정 시각
            'Y',             # 사용 여부
            1                # 표시 순서 (기본값 1)
        ))

        conn.commit()
        print(f"[DB] Problem saved: {problem['id']} - {problem['project_title']}")

    except Exception as e:
        conn.rollback()
        print(f"[DB ERROR] Failed to save problem: {e}")
        raise

    finally:
        cursor.close()
        conn.close()


def test_db_connection():
    """DB 연결 테스트"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"[DB] Connection successful: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] Connection failed: {e}")
        return False


if __name__ == "__main__":
    # DB 연결 테스트
    test_db_connection()
