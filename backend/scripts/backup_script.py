"""DB 전체 데이터를 JSON으로 백업하는 스크립트 (1회성 유틸리티)."""
import os
import django
import json
import json.encoder

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import UserProfile, UserDetail
from django.contrib.auth.models import User

def backup():
    data = {
        'users': [],
        'profiles': [],
        'details': []
    }
    
    # Backup auth.User
    for u in User.objects.all():
        data['users'].append({
            'username': u.username,
            'email': u.email,
            'password': u.password,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'is_staff': u.is_staff,
            'is_active': u.is_active,
            'is_superuser': u.is_superuser,
            'date_joined': str(u.date_joined),
        })

    # Backup UserProfile
    for p in UserProfile.objects.all():
        data['profiles'].append({
            'old_id': p.id,
            'user_name': p.user_name,
            'user_nickname': p.user_nickname,
            'email': p.email,
            'birth_date': str(p.birth_date) if p.birth_date else None,
            'password': p.password,
            'create_id': p.create_id,
            'update_id': p.update_id,
        })

    # Backup UserDetail
    for d in UserDetail.objects.all():
        data['details'].append({
            'user_old_id': d.user.id,
            'is_developer': d.is_developer,
            'job_role': d.job_role,
            'interests': d.interests,
        })

    backup_path = os.path.join(os.path.dirname(__file__), 'backup_data.json')
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Backup completed: {backup_path}")

if __name__ == '__main__':
    backup()
