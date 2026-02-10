import os
import boto3
import requests
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def update_rds_security_group(group_id=None, port=5432):
    """
    현재 공인 IP를 AWS RDS 보안 그룹의 인바운드 규칙에 등록합니다.
    """
    # 1. AWS 설정 가져오기
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_S3_REGION_NAME", "ap-northeast-2")
    
    # 보안 그룹 ID (제공해주신 ID가 있다면 우선 사용)
    # 실제 환경에 맞춰 sg-xxxxxxxxxxxx 부분을 수정하거나 환경 변수로 관리하세요.
    target_group_id = group_id or "sg-0a7ae2d0ad8393440" # 예시 ID

    if not all([access_key, secret_key]):
        print("❌ 에러: AWS 인증 정보가 .env에 없습니다.")
        return

    # 2. 현재 공인 IP 가져오기
    try:
        current_ip = requests.get("https://api.ipify.org").text
        cidr_ip = f"{current_ip}/32"
        print(f"🔍 현재 공인 IP 감지됨: {current_ip}")
    except Exception as e:
        print(f"❌ 에리: 현재 IP를 가져오지 못했습니다: {e}")
        return

    # 3. Boto3 EC2 클라이언트 생성 (보안 그룹은 EC2 서비스 범주)
    ec2 = boto3.client(
        'ec2',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

    # 4. 보안 그룹 규칙 추가
    try:
        print(f"🚀 보안 그룹({target_group_id})에 IP 등록 시도 중...")
        ec2.authorize_security_group_ingress(
            GroupId=target_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': port,
                    'ToPort': port,
                    'IpRanges': [
                        {
                            'CidrIp': cidr_ip,
                            'Description': f'Added by Automation Script ({current_ip})'
                        },
                    ],
                },
            ]
        )
        print(f"✅ 성공! 현재 IP({current_ip})가 포트 {port}에 대해 허용되었습니다.")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidPermission.Duplicate':
            print(f"ℹ️ 알림: 이미 등록된 IP 주소입니다 ({cidr_ip}).")
        else:
            print(f"❌ AWS 에러 발생: {e}")
    except Exception as e:
        print(f"❌ 알 수 없는 에러 발생: {e}")

if __name__ == "__main__":
    # 실행 시 보안 그룹 ID를 인자로 넘기거나, 소스코드 내 기본값을 수정하세요.
    update_rds_security_group()
