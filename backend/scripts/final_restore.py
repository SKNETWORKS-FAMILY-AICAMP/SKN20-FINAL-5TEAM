"""백업된 JSON 데이터를 DB에 최종 복원하는 스크립트 (1회성 유틸리티)."""
import os
import django
import json
from django.db import connection, transaction

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import UserProfile, UserDetail
from django.contrib.auth.models import User

def final_repair_and_restore():
    with connection.cursor() as cursor:
        print("--- Step 1: Cleaning up constraints and tables ---")
        cursor.execute("ALTER TABLE gym_userdetail DROP CONSTRAINT IF EXISTS gym_userdetail_user_id_fkey")
        cursor.execute("TRUNCATE TABLE gym_userdetail CASCADE")
        cursor.execute("TRUNCATE TABLE gym_user CASCADE")
        
        print("--- Step 2: Dropping identity and forcing column type change ---")
        # Drop identity property first
        try:
            cursor.execute("ALTER TABLE gym_user ALTER COLUMN id DROP IDENTITY IF EXISTS")
        except Exception as e:
            print(f"Note: Identity drop might have failed if it didn't exist: {e}")

        # Now alter column types
        cursor.execute("ALTER TABLE gym_user ALTER COLUMN id TYPE varchar(50) USING id::varchar")
        cursor.execute("ALTER TABLE gym_userdetail ALTER COLUMN user_id TYPE varchar(50) USING user_id::varchar")
        
        print("--- Step 3: Verifying column types ---")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'gym_user' AND column_name = 'id'
        """)
        print(f"gym_user.id type: {cursor.fetchone()}")

        print("--- Step 4: Restoring constraints ---")
        cursor.execute("ALTER TABLE gym_userdetail ADD CONSTRAINT gym_userdetail_user_id_fkey FOREIGN KEY (user_id) REFERENCES gym_user(id) ON DELETE CASCADE")

    print("--- Step 5: Restoring data from backup ---")
    backup_path = os.path.join(os.path.dirname(__file__), 'backup_data.json')
    if not os.path.exists(backup_path):
        print("Backup file not found!")
        return

    with open(backup_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    try:
        with transaction.atomic():
            for p_data in data['profiles']:
                p = UserProfile.objects.create(
                    id=p_data['old_id'],
                    user_name=p_data['user_name'],
                    user_nickname=p_data['user_nickname'],
                    email=p_data['email'],
                    birth_date=p_data['birth_date'] if p_data['birth_date'] != 'None' else None,
                    password=p_data['password'],
                    create_id=p_data['create_id'],
                    update_id=p_data['update_id']
                )
                print(f"Restored Profile: {p.id}")

            for d_data in data['details']:
                UserDetail.objects.create(
                    user_id=d_data['user_old_id'],
                    is_developer=d_data['is_developer'],
                    job_role=d_data['job_role'],
                    interests=d_data['interests']
                )
                print(f"Restored Detail for: {d_data['user_old_id']}")

            # Re-sync auth.User usernames
            for u_data in data['users']:
                try:
                    u = User.objects.get(email=u_data['email'])
                    u.username = u_data['username']
                    u.save()
                    print(f"Reverted auth.User: {u.username}")
                except User.DoesNotExist:
                    User.objects.create_user(
                        username=u_data['username'],
                        email=u_data['email'],
                        password='temp'
                    ).password = u_data['password']
                    print(f"Recreated auth.User: {u_data['username']}")

    except Exception as e:
        print(f"Error during restoration: {e}")
        return

    print("Final repair and restoration completed successfully.")

if __name__ == '__main__':
    final_repair_and_restore()
