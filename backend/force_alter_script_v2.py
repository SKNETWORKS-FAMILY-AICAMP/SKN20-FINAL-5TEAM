import os
import django
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def force_alter_v2():
    with connection.cursor() as cursor:
        print("Checking current schema...")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'gym_user' AND column_name = 'id'
        """)
        row = cursor.fetchone()
        print(f"Current id type: {row}")

        print("Forcing schema alter v2...")
        # Drop all possible constraints
        cursor.execute("ALTER TABLE gym_userdetail DROP CONSTRAINT IF EXISTS gym_userdetail_user_id_fkey")
        
        # Force alter with USING clause just in case
        cursor.execute("ALTER TABLE gym_user ALTER COLUMN id TYPE varchar(50) USING id::varchar")
        cursor.execute("ALTER TABLE gym_userdetail ALTER COLUMN user_id TYPE varchar(50) USING user_id::varchar")
        
        # Restore constraints
        cursor.execute("ALTER TABLE gym_userdetail ADD CONSTRAINT gym_userdetail_user_id_fkey FOREIGN KEY (user_id) REFERENCES gym_user(id) ON DELETE CASCADE")
        
    print("Schema alter forced successfully.")

if __name__ == '__main__':
    force_alter_v2()
