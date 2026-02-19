# Job Planner Agent

채용공고 분석 및 취업 전략 수립 에이전트 (원본 v3.1 기반)

## 🎯 기능

- 스킬 매칭 (sentence-transformers)
- LLM 기반 전략 추천 (GPT-4o-mini)
- 대화형 에이전트 루프

## 📦 설치

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경변수 설정
export OPENAI_API_KEY=sk-...
```

## 🚀 실행

```bash
python main.py
```

## 📁 구조

```
job-planner-agent/
├── main.py              # 실행 파일
├── config.py            # 설정
├── agent/
│   ├── models.py        # 데이터 모델
│   ├── state.py         # 상태 관리
│   ├── planner.py       # 전략 추천
│   └── orchestrator.py  # 메인 루프
├── scoring/
│   └── engine.py        # 스킬 매칭
└── llm/
    └── gateway.py       # LLM 연동
```

## ✅ 현재 구현된 기능

- [x] 스킬 매칭 (ScoringEngine)
- [x] LLM 전략 추천 (Planner)
- [x] 에이전트 루프 (Orchestrator)
- [x] 상태 관리 (State)

## 📝 원본 설계 문서

`job-planner-agent-v3.1 (1).md` 참조
