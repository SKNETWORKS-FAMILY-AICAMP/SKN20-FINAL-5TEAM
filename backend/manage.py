#!/usr/bin/env python
# 수정일: 2026-01-20
# 수정내용: Django 관리 명령줄 유틸리티 생성
# Django 프로젝트의 뼈대이자 명령어 실행기입니다. 
# 서버를 켜거나(runserver), 데이터베이스를 세팅(migrate)할 때 사용하는 스크립트

import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
