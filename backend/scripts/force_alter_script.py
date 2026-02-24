"""DB 스키마를 강제로 변경(ALTER)하는 스크립트 v1 (1회성 유틸리티)."""
import os
import django
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def force_alter():
    with connection.cursor() as cursor:
        print("Forcing schema alter...")
        # 1. Drop constraints that might block the alter
        cursor.execute("ALTER TABLE gym_userdetail DROP CONSTRAINT IF EXISTS gym_userdetail_user_id_fkey")
        
        # 2. Alter column types
        cursor.execute("ALTER TABLE gym_user ALTER COLUMN id TYPE varchar(50)")
        cursor.execute("ALTER TABLE gym_userdetail ALTER COLUMN user_id TYPE varchar(50)")
        
        # 3. Restore constraints
        cursor.execute("ALTER TABLE gym_userdetail ADD CONSTRAINT gym_userdetail_user_id_fkey FOREIGN KEY (user_id) REFERENCES gym_user(id) ON DELETE CASCADE")
        print("Schema alter forced successfully.")

if __name__ == '__main__':
    force_alter()
