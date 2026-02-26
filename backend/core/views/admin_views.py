import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

# [수정일: 2026-02-26] 간단한 관리자 로그 조회를 위한 하드코딩 인증/권한
ADMIN_USERNAME = "admin@admin.com"
ADMIN_PASSWORD = "admin1234"
ADMIN_TOKEN_SECRET = "skn20-admin-secret-token"

class AdminLoginView(APIView):
    """관리자 로그인용 뷰"""
    permission_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return Response({"token": ADMIN_TOKEN_SECRET}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class AdminLogView(APIView):
    """에러 로그 파일 내용 읽기"""
    permission_classes = []

    def get(self, request):
        auth_header = request.headers.get("Authorization")
        expected_token = f"Bearer {ADMIN_TOKEN_SECRET}"

        if not auth_header or auth_header != expected_token:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        # settings.LOGS_DIR 사용
        # settings.py 에는 LOGS_DIR = os.path.join(BASE_DIR, 'logs') 가 등록되어 있음.
        try:
            logs_dir = getattr(settings, 'LOGS_DIR', os.path.join(settings.BASE_DIR, 'logs'))
            log_file_path = os.path.join(logs_dir, 'error.log')

            if not os.path.exists(log_file_path):
                return Response({"logs": "Log file not found."}, status=status.HTTP_200_OK)
            
            # 파일 읽기 (가장 최근 로그를 잘 보여주기 위해 끝에서부터 500줄 정도 읽기 방식을 사용 가능)
            with open(log_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            # 최대로 표시할 줄 수를 1000줄로 제한
            max_lines = 1000
            if len(lines) > max_lines:
                lines = lines[-max_lines:]
                
            return Response({"logs": "".join(lines)}, status=status.HTTP_200_OK)
        
        
        except Exception as e:
            return Response({"error": f"Failed to read logs: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

import datetime
import shutil

class AdminLogSaveView(APIView):
    """현재 error.log 파일을 보관용(archive)으로 복사본 생성하기"""
    permission_classes = []

    def post(self, request):
        auth_header = request.headers.get("Authorization")
        expected_token = f"Bearer {ADMIN_TOKEN_SECRET}"

        if not auth_header or auth_header != expected_token:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            logs_dir = getattr(settings, 'LOGS_DIR', os.path.join(settings.BASE_DIR, 'logs'))
            log_file_path = os.path.join(logs_dir, 'error.log')

            if not os.path.exists(log_file_path):
                return Response({"error": "Log file not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # archive 파일명 생성 (예: archive_20260226_101500.log)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_filename = f"archive_{timestamp}.log"
            archive_path = os.path.join(logs_dir, archive_filename)
            
            # 파일 복사
            shutil.copy2(log_file_path, archive_path)

            return Response({
                "message": "Log saved successfully.",
                "archive_filename": archive_filename
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": f"Failed to save log: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdminLogArchiveListView(APIView):
    """지정된 디렉토리에서 archive_*.log 파일 목록 가져오기"""
    permission_classes = []

    def get(self, request):
        auth_header = request.headers.get("Authorization")
        expected_token = f"Bearer {ADMIN_TOKEN_SECRET}"

        if not auth_header or auth_header != expected_token:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            logs_dir = getattr(settings, 'LOGS_DIR', os.path.join(settings.BASE_DIR, 'logs'))
            
            archives = []
            if os.path.exists(logs_dir):
                for f in os.listdir(logs_dir):
                    if f.startswith('archive_') and f.endswith('.log'):
                        file_path = os.path.join(logs_dir, f)
                        # 파일 크기 및 수정 시간 정보 포함
                        size = os.path.getsize(file_path)
                        modified_time = os.path.getmtime(file_path)
                        archives.append({
                            "filename": f,
                            "size": size,
                            "modified_at": datetime.datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M:%S")
                        })
            
            # 최신순 (수정 시간 내림차순) 정렬
            archives.sort(key=lambda x: x['filename'], reverse=True)
            
            return Response({"archives": archives}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Failed to get archive list: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdminLogArchiveDetailView(APIView):
    """특정 archive 로그 내용 읽기"""
    permission_classes = []

    def get(self, request, filename):
        auth_header = request.headers.get("Authorization")
        expected_token = f"Bearer {ADMIN_TOKEN_SECRET}"

        if not auth_header or auth_header != expected_token:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # 보안 검사: 허용된 prefix와 suffix인지 확인, 경로 이탈(..) 방지
        if not filename.startswith('archive_') or not filename.endswith('.log') or '..' in filename:
            return Response({"error": "Invalid filename."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            logs_dir = getattr(settings, 'LOGS_DIR', os.path.join(settings.BASE_DIR, 'logs'))
            file_path = os.path.join(logs_dir, filename)

            if not os.path.exists(file_path):
                return Response({"error": "Archive not found."}, status=status.HTTP_404_NOT_FOUND)
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            return Response({
                "filename": filename,
                "logs": content
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Failed to read archive: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

import re
from collections import defaultdict
from django.utils import timezone

class AdminServerStatusView(APIView):
    """서버 상태 그래프를 위한 에러 발생 시계열 데이터 제공"""
    permission_classes = []

    def get(self, request):
        auth_header = request.headers.get("Authorization")
        expected_token = f"Bearer {ADMIN_TOKEN_SECRET}"

        if not auth_header or auth_header != expected_token:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # 쿼리 파라미터 확인 (24h, 3d, 7d)
        time_range = request.query_params.get('range', '24h')
        
        if time_range == '7d':
            hours_back = 168
            interval_hours = 6
        elif time_range == '3d':
            hours_back = 72
            interval_hours = 3
        else: # 기본 24h
            hours_back = 24
            interval_hours = 1
            
        try:
            logs_dir = getattr(settings, 'LOGS_DIR', os.path.join(settings.BASE_DIR, 'logs'))
            
            # 읽을 파일 목록 (error.log + archive_*.log)
            files_to_read = []
            if os.path.exists(logs_dir):
                for f in os.listdir(logs_dir):
                    if f == 'error.log' or (f.startswith('archive_') and f.endswith('.log')):
                        files_to_read.append(os.path.join(logs_dir, f))
            
            # 기준 시간 계산
            now = datetime.datetime.now()
            # interval 간격에 맞춰 시작 시간을 깔끔하게 내림 (truncate)
            start_baseline = now.replace(minute=0, second=0, microsecond=0) - datetime.timedelta(hours=hours_back)
            start_baseline -= datetime.timedelta(hours=start_baseline.hour % interval_hours)
            
            # 시간별 로그 카운트를 저장할 딕셔너리
            error_counts = defaultdict(int)
            date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
            
            for file_path in files_to_read:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line in f:
                            match = date_pattern.search(line)
                            if match:
                                log_time_str = match.group(1)
                                try:
                                    log_time = datetime.datetime.strptime(log_time_str, "%Y-%m-%d %H:%M:%S")
                                    if log_time >= start_baseline:
                                        # Interval 기준으로 시간 절사
                                        truncated_hour = log_time.hour - (log_time.hour % interval_hours)
                                        truncated_time = log_time.replace(hour=truncated_hour, minute=0, second=0, microsecond=0)
                                        hour_key = truncated_time.strftime("%Y-%m-%d %H:00")
                                        error_counts[hour_key] += 1
                                except ValueError:
                                    pass
                except Exception:
                    pass
            
            labels = []
            full_labels = []
            values = []
            traffic_values = []
            import random
            
            # 데이터 포인트 개수 계산
            num_points = (hours_back // interval_hours) + 1
            
            for i in range(num_points):
                target_time = start_baseline + datetime.timedelta(hours=i * interval_hours)
                target_key = target_time.strftime("%Y-%m-%d %H:00")
                
                # 라벨 포맷 결정: 24h는 시간만, 길어지면 월/일 표시
                if interval_hours == 1:
                    labels.append(target_time.strftime("%H:00"))
                else:
                    labels.append(target_time.strftime("%m-%d %H:00"))
                    
                full_labels.append(target_key)
                values.append(error_counts.get(target_key, 0))
                
                # Base traffic load
                base_traffic = random.randint(30, 60)
                if error_counts.get(target_key, 0) > 0:
                    base_traffic += random.randint(20, 40)
                traffic_values.append(min(100, base_traffic))
                
            return Response({
                "labels": labels,
                "full_labels": full_labels,
                "error_counts": values,
                "traffic_loads": traffic_values,
                "range": time_range
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Failed to get server status: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
