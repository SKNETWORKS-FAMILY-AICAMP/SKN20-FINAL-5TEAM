"""
PyTorch 트랙 문제 출제 스펙 정의
P1 Progressive 문제 (3단계) 생성을 위한 스펙
"""

# 트랙별 설정 통합 관리 (확장성 확보)
TRACK_SPECS = {
    "pytorch_mnist": {
        "track_name": "PyTorch MNIST 분류",
        "difficulty": 2,
        "context": "MNIST 손글씨 분류 모델 학습 중 에러 발생",
        "tech_stack": "PyTorch",
        "steps": [
            {"step": 1, "bug_type_name": "Shape Error", "allowed_bugs": ["reshape", "view", "flatten"]},
            {"step": 2, "bug_type_name": "Training Loop Error", "allowed_bugs": ["zero_grad", "step", "backward"]},
            {"step": 3, "bug_type_name": "Evaluation Error", "allowed_bugs": ["eval_mode", "no_grad"]}
        ]
    },
    "pandas_data_cleaning": {
        "track_name": "Pandas 데이터 전처리",
        "difficulty": 2,
        "context": "사용자 로그 데이터 전처리 파이프라인 오류",
        "tech_stack": "Pandas",
        "steps": [
            {"step": 1, "bug_type_name": "Missing Value Handling", "allowed_bugs": ["fillna", "dropna"]},
            {"step": 2, "bug_type_name": "Data Type Conflict", "allowed_bugs": ["astype", "infer_objects"]},
            {"step": 3, "bug_type_name": "Logical Filtering", "allowed_bugs": ["copy", "inplace", "boolean_indexing"]}
        ]
    }
}

# 기본값 (하위 호환성 유지)
PYTORCH_TRACK = TRACK_SPECS["pytorch_mnist"]
