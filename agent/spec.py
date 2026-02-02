"""
PyTorch 트랙 문제 출제 스펙 정의
P1 Progressive 문제 (3단계) 생성을 위한 스펙
"""

# 트랙별 설정 통합 관리 (확장성 확보)
TRACK_SPECS = {
    "pytorch_basic": {
        "track_name": "PyTorch 기초 모델링",
        "difficulty": 1,
        "context": "간단한 수치 예측용 MLP(Multi-Layer Perceptron) 모델 구현 중 문제 발생",
        "tech_stack": "PyTorch",
        "steps": [
            {"step": 1, "bug_type_name": "Initialization Error", "allowed_bugs": ["weight_init", "layer_size_mismatch"]},
            {"step": 2, "bug_type_name": "Activation/Loss Error", "allowed_bugs": ["relu_missing", "cross_entropy_for_regression"]},
            {"step": 3, "bug_type_name": "Overfitting/Regularization", "allowed_bugs": ["dropout_always_on", "weight_decay"]}
        ],
        "thinking_objectives": [
            {
                "step": 1,
                "objective": "architecture_verification",
                "description": "네트워크 구조 검증 사고",
                "validation": "layer dimension 계산 없이는 해결 불가",
                "required_in_hint": ["차원", "크기", "layer"]
            },
            {
                "step": 2,
                "objective": "loss_function_matching",
                "description": "손실 함수와 태스크 일치성 판단",
                "validation": "regression vs classification 구분 필수",
                "required_in_hint": ["손실", "loss", "함수"]
            },
            {
                "step": 3,
                "objective": "overfitting_diagnosis",
                "description": "과적합 원인 진단 사고",
                "validation": "train/val loss 비교 분석 필수",
                "required_in_hint": ["과적합", "정규화", "드롭아웃"]
            }
        ]
    },
    "pytorch_mnist": {
        "track_name": "PyTorch CNN 이미지 분류",
        "difficulty": 2,
        "context": "CNN 기반 MNIST 데이터 학습 파이프라인 오류 (주의: 검증 시에는 실제 MNIST 대신 torch.randn(batch, 1, 28, 28) 사용)",
        "tech_stack": "PyTorch",
        "steps": [
            {"step": 1, "bug_type_name": "Feature Dimension Error", "allowed_bugs": ["convolution_padding", "pooling_stride", "flatten"]},
            {"step": 2, "bug_type_name": "Gradient Flow Error", "allowed_bugs": ["require_grad_false", "zero_grad_position"]},
            {"step": 3, "bug_type_name": "Inference Switch Error", "allowed_bugs": ["train_eval_mode", "batch_norm_update"]}
        ],
        "thinking_objectives": [
            {
                "step": 1,
                "objective": "shape_trace",
                "description": "CNN 레이어 통과 시 텐서 차원 역추적 사고",
                "validation": "conv/pool 연산 후 shape 계산 없이는 해결 불가",
                "required_in_hint": ["차원", "shape", "크기", "flatten"]
            },
            {
                "step": 2,
                "objective": "gradient_flow_analysis",
                "description": "역전파 흐름 분석 사고",
                "validation": "gradient 업데이트 순서 이해 필수",
                "required_in_hint": ["gradient", "역전파", "zero_grad"]
            },
            {
                "step": 3,
                "objective": "train_eval_mode_distinction",
                "description": "학습/평가 모드 차이 이해",
                "validation": "dropout/batch_norm 동작 차이 이해 필수",
                "required_in_hint": ["eval", "train", "모드"]
            }
        ]
    },
    "pandas_data_cleaning": {
        "track_name": "Pandas 실무 데이터 전처리",
        "difficulty": 2,
        "context": "실제 비정형 로그 데이터 정제 및 파이프라인 구현 오류",
        "tech_stack": "Pandas",
        "steps": [
            {"step": 1, "bug_type_name": "Data Consistency Error", "allowed_bugs": ["null_handling", "duplicate_detection"]},
            {"step": 2, "bug_type_name": "Type Conversion Bug", "allowed_bugs": ["datetime_parsing", "categorical_encoding"]},
            {"step": 3, "bug_type_name": "Aggregation Logic Error", "allowed_bugs": ["groupby_agg_mismatch", "pivot_table_indices"]}
        ],
        "thinking_objectives": [
            {
                "step": 1,
                "objective": "data_quality_assessment",
                "description": "데이터 무결성 검증 사고",
                "validation": "null 패턴 분석 없이는 해결 불가",
                "required_in_hint": ["결측치", "null", "중복"]
            },
            {
                "step": 2,
                "objective": "type_inference",
                "description": "데이터 타입 추론 및 변환 사고",
                "validation": "타입 불일치 원인 추적 필수",
                "required_in_hint": ["타입", "변환", "형식"]
            },
            {
                "step": 3,
                "objective": "aggregation_logic_verification",
                "description": "집계 로직 검증 사고",
                "validation": "groupby 결과 예측 필수",
                "required_in_hint": ["집계", "groupby", "그룹"]
            }
        ]
    }
}

# 기본값 (하위 호환성 유지)
PYTORCH_TRACK = TRACK_SPECS["pytorch_mnist"]
