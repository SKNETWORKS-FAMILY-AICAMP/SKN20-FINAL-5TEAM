import os
import django
import json
from django.db import connection, transaction

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import UserProfile, UserDetail
from django.contrib.auth.models import User

def dynamic_repair_and_restore():
    with connection.cursor() as cursor:
        print("--- Step 1: Dynamically dropping all constraints ---")
        # Find and drop all constraints involving these tables
        for table in ['gym_userdetail', 'gym_user']:
            cursor.execute(f"""
                SELECT conname 
                FROM pg_constraint 
                WHERE conrelid = '{table}'::regclass
            """)
            for (conname,) in cursor.fetchall():
                print(f"Dropping constraint {conname} from {table}...")
                cursor.execute(f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {conname} CASCADE")

        print("--- Step 2: Truncating tables ---")
        cursor.execute("TRUNCATE TABLE gym_userdetail CASCADE")
        cursor.execute("TRUNCATE TABLE gym_user CASCADE")
        
        print("--- Step 3: Dropping identity and forcing column type change ---")
        try:
            cursor.execute("ALTER TABLE gym_user ALTER COLUMN id DROP IDENTITY IF EXISTS")
        except Exception as e:
            print(f"Note: Identity drop might have failed: {e}")

        cursor.execute("ALTER TABLE gym_user ALTER COLUMN id TYPE varchar(50) USING id::varchar")
        cursor.execute("ALTER TABLE gym_userdetail ALTER COLUMN user_id TYPE varchar(50) USING user_id::varchar")
        
        print("--- Step 4: Restoring basic constraints ---")
        # We need the primary keys back
        cursor.execute("ALTER TABLE gym_user ADD PRIMARY KEY (id)")
        cursor.execute("ALTER TABLE gym_userdetail ADD PRIMARY KEY (user_id)")
        cursor.execute("ALTER TABLE gym_userdetail ADD CONSTRAINT gym_userdetail_user_id_fkey FOREIGN KEY (user_id) REFERENCES gym_user(id) ON DELETE CASCADE")

    print("--- Step 5: Restoring data from backup ---")
    if not os.path.exists('backup_data.json'):
        print("Backup file not found!")
        return

    with open('backup_data.json', 'r', encoding='utf-8') as f:
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

    print("Dynamic repair and restoration completed successfully.")

if __name__ == '__main__':
    dynamic_repair_and_restore()
