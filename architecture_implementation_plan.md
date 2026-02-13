# 시스템 아키텍처 문제 DB 등록 및 제출 구현 계획

## 📋 개요
`architecture_advanced_gcp.json` 파일의 GCP 아키텍처 문제를 DB에 등록하고, 사용자가 문제를 풀고 제출할 때 `gym_user_solved_problem` 테이블에 데이터를 저장하는 전체 프로세스를 구현합니다.

---

## 🔍 현재 상태 분석

### 데이터 구조
- **JSON 파일**: `frontend/src/data/architecture_advanced_gcp.json`
  - 각 문제는 `problem_id`, `title`, `scenario`, `rubric_functional`, `axis_weights` 등의 필드를 포함
  - 54,379 토큰 크기의 대용량 파일

### DB 모델
- **Practice 모델** (`gym_practice`): 유닛 단위 관리
  - `id`: 문자열 (예: "unit01", "unit02")
  - `title`, `subtitle`, `max_points` 등

- **PracticeDetail 모델** (`gym_practice_detail`): 개별 문제 관리
  - `id`: 문자열 (예: "unit0101", "unit0102")
  - `practice`: ForeignKey to Practice
  - `content_data`: JSONField (문제 데이터 저장)
  - `detail_type`: 'PROBLEM', 'CHATTING', 'REFERENCE'

- **UserSolvedProblem 모델** (`gym_user_solved_problem`): 사용자 제출 기록
  - `user`: ForeignKey to UserProfile
  - `practice_detail`: ForeignKey to PracticeDetail
  - `score`: 획득 점수
  - `submitted_data`: JSONField (사용자 제출 데이터)
  - `is_perfect`: 만점 여부
  - unique_together: ('user', 'practice_detail')

### 제출 데이터 형식 (프론트엔드)
```json
{
  "mission_id": "adv_001_amazon_ranking_system",
  "completed_steps": 3,
  "total_steps": 5,
  "hint_used": 2,
  "retry_count": 1
}
```

### 기존 API 엔드포인트
- **POST** `/api/core/activity/submit/`
  - 현재 구현: SubmitProblemView
  - 요청 필드: `detail_id`, `score`, `submitted_data`

---

## 📝 구현 단계

### **Phase 1: DB 데이터 준비**

#### Step 1-1: Practice 유닛 생성
**목표**: 시스템 아키텍처 전용 유닛 생성

**작업**:
1. Django 관리자 페이지 또는 migration 스크립트로 Practice 레코드 생성
2. 필드 값 예시:
   ```python
   Practice.objects.create(
       id='unit05',
       unit_number=5,
       level=20,
       title='System Architecture Design',
       subtitle='GCP 기반 대규모 시스템 설계',
       max_points=10000,
       color_code='#FF6B35',
       icon_name='network',
       is_active=True
   )
   ```

**체크포인트**:
- [ ] Practice 레코드가 `gym_practice` 테이블에 생성됨
- [ ] 관리자 페이지에서 유닛이 조회됨

---

#### Step 1-2: JSON 데이터 파싱 스크립트 작성
**목표**: JSON 파일을 읽어서 PracticeDetail 레코드로 변환

**작업**:
1. `backend/scripts/load_architecture_problems.py` 스크립트 생성
2. JSON 파싱 로직 구현:
   ```python
   import json
   from core.models import Practice, PracticeDetail

   def load_gcp_problems():
       with open('frontend/src/data/architecture_advanced_gcp.json', 'r', encoding='utf-8') as f:
           problems = json.load(f)

       practice = Practice.objects.get(id='unit05')

       for idx, problem in enumerate(problems, start=1):
           detail_id = f'unit05{idx:02d}'  # unit0501, unit0502, ...

           PracticeDetail.objects.update_or_create(
               id=detail_id,
               defaults={
                   'practice': practice,
                   'detail_title': problem['title'],
                   'detail_type': 'PROBLEM',
                   'content_data': problem,  # 전체 문제 데이터를 JSON으로 저장
                   'display_order': idx,
                   'is_active': True
               }
           )
   ```

3. 스크립트 실행:
   ```bash
   python manage.py shell < backend/scripts/load_architecture_problems.py
   ```

**체크포인트**:
- [ ] 스크립트가 에러 없이 실행됨
- [ ] `gym_practice_detail` 테이블에 모든 문제가 삽입됨
- [ ] `content_data` 필드에 JSON이 정상적으로 저장됨

---

### **Phase 2: 프론트엔드 데이터 fetching**

#### Step 2-1: API 서비스 함수 수정
**목표**: PracticeDetail에서 문제 목록을 가져오도록 수정

**작업**:
1. `frontend/src/features/practice/architecture/services/architectureApiFastTest.js` 수정
2. 기존 로컬 JSON 파일 대신 백엔드 API 호출:
   ```javascript
   export async function fetchProblems() {
     const response = await axios.get('/api/core/practices/unit05/details/');
     return response.data.map(detail => ({
       ...detail.content_data,
       practice_detail_id: detail.id  // DB ID를 추가로 저장
     }));
   }
   ```

**체크포인트**:
- [ ] API 호출이 성공적으로 이루어짐
- [ ] 문제 리스트가 정상적으로 로드됨

---

#### Step 2-2: 백엔드 API 엔드포인트 추가
**목표**: 특정 Practice의 상세 목록을 반환하는 API 생성

**작업**:
1. `backend/core/views/practice_view.py`에 뷰 추가:
   ```python
   class PracticeDetailListView(APIView):
       permission_classes = [permissions.AllowAny]

       def get(self, request, practice_id):
           details = PracticeDetail.objects.filter(
               practice_id=practice_id,
               is_active=True
           ).order_by('display_order')

           data = [{
               'id': d.id,
               'detail_title': d.detail_title,
               'content_data': d.content_data
           } for d in details]

           return Response(data, status=status.HTTP_200_OK)
   ```

2. `backend/core/urls.py`에 라우트 추가:
   ```python
   path('practices/<str:practice_id>/details/',
        PracticeDetailListView.as_view(),
        name='practice_details'),
   ```

**체크포인트**:
- [ ] API 엔드포인트가 정상 작동
- [ ] `/api/core/practices/unit05/details/` 호출 시 문제 목록 반환

---

### **Phase 3: 제출 로직 통합**

#### Step 3-1: 프론트엔드 제출 데이터 구성
**목표**: 아키텍처 문제 제출 시 필요한 데이터 형식 정의

**작업**:
1. `SystemArchitecturePractice.vue` 또는 evaluation composable에서 제출 로직 수정
2. 제출 데이터 구조 확정:
   ```javascript
   const submitData = {
     detail_id: currentProblem.practice_detail_id,  // DB ID
     score: evaluationResult.totalScore,
     submitted_data: {
       problem_id: currentProblem.problem_id,  // JSON의 원본 ID
       components: droppedComponents.value,
       connections: connections.value,
       mermaid_code: mermaidCode.value,
       deep_dive_answers: deepDiveAnswers.value,
       hint_used: Object.values(hintUsed.value).filter(v => v).length,
       retry_count: retryCount.value,
       evaluation_result: evaluationResult
     }
   };

   await axios.post('/api/core/activity/submit/', submitData);
   ```

**체크포인트**:
- [ ] 제출 시 `detail_id`가 올바르게 전달됨
- [ ] `submitted_data`에 필요한 모든 정보가 포함됨

---

#### Step 3-2: 백엔드 제출 처리 검증
**목표**: 기존 SubmitProblemView가 아키텍처 데이터를 올바르게 처리하는지 확인

**작업**:
1. `backend/core/views/activity_view.py` 의 `SubmitProblemView` 확인
2. 현재 구현이 이미 JSONField에 데이터를 저장하므로 **추가 수정 불필요**
3. 필요시 로깅 추가:
   ```python
   import logging
   logger = logging.getLogger(__name__)

   def post(self, request):
       logger.info(f"Architecture submission: {request.data}")
       # 기존 로직...
   ```

**체크포인트**:
- [ ] 제출 후 `gym_user_solved_problem` 테이블에 레코드 생성됨
- [ ] `submitted_data` 필드에 JSON이 올바르게 저장됨
- [ ] `UserActivity`의 `total_points`가 업데이트됨

---

### **Phase 4: 통합 테스트**

#### Step 4-1: End-to-End 테스트
**목표**: 전체 플로우가 정상 작동하는지 확인

**테스트 시나리오**:
1. 프론트엔드에서 시스템 아키텍처 유닛 접속
2. 문제 리스트가 DB에서 로드되는지 확인
3. 특정 문제 선택 및 아키텍처 설계
4. 평가 실행 후 제출
5. 제출 후 다음 확인:
   - `gym_user_solved_problem`에 레코드 생성됨
   - `submitted_data`에 설계 정보가 포함됨
   - 리더보드에 점수 반영됨

**체크포인트**:
- [ ] 모든 단계가 에러 없이 진행됨
- [ ] 제출 데이터가 DB에 정확히 저장됨
- [ ] 재제출 시 `update_or_create`로 기존 레코드 업데이트됨

---

#### Step 4-2: 예외 상황 처리
**목표**: 에러 케이스 대응

**테스트 케이스**:
1. 존재하지 않는 `detail_id` 제출
   - 응답: `404 Not Found`
2. 필수 필드 누락 (`score` 없음)
   - 응답: `400 Bad Request`
3. 중복 제출 (같은 문제 재제출)
   - 동작: 기존 레코드 업데이트

**체크포인트**:
- [ ] 모든 예외 상황에서 적절한 에러 응답 반환
- [ ] 로그에 에러 정보가 기록됨

---

### **Phase 5: 데이터 마이그레이션 (선택사항)**

#### Step 5-1: 기존 데이터 마이그레이션
**목표**: 이전에 로컬 JSON으로 제출된 데이터가 있다면 DB 형식으로 변환

**작업**:
1. 마이그레이션 스크립트 작성 (필요시)
2. 기존 `submitted_data`의 `mission_id`를 `practice_detail_id`로 매핑

**체크포인트**:
- [ ] 기존 데이터가 새 형식으로 변환됨

---

## 🎯 최종 검증 체크리스트

### DB 레벨
- [ ] `gym_practice` 테이블에 시스템 아키텍처 유닛 존재
- [ ] `gym_practice_detail` 테이블에 모든 GCP 문제 저장됨
- [ ] `gym_user_solved_problem` 테이블에 제출 기록 저장됨

### API 레벨
- [ ] `GET /api/core/practices/unit05/details/` 정상 작동
- [ ] `POST /api/core/activity/submit/` 아키텍처 데이터 처리 가능

### 프론트엔드 레벨
- [ ] 문제 목록이 DB에서 로드됨
- [ ] 제출 시 올바른 `detail_id` 전달
- [ ] 제출 후 결과 화면 정상 표시

### 통합 레벨
- [ ] End-to-End 플로우 성공
- [ ] 리더보드에 점수 반영
- [ ] 재제출 시 업데이트 정상 작동

---

## 🚀 예상 소요 시간

| Phase | 예상 시간 |
|-------|----------|
| Phase 1: DB 데이터 준비 | 1-2시간 |
| Phase 2: 프론트엔드 연동 | 1시간 |
| Phase 3: 제출 로직 통합 | 1-2시간 |
| Phase 4: 통합 테스트 | 1시간 |
| **총계** | **4-6시간** |

---

## 📌 주의사항

1. **JSON 파일 크기**: 54,379 토큰이므로 한 번에 읽기 어려움
   - 파일을 청크 단위로 읽거나, 필요한 필드만 추출하는 방식 고려

2. **ID 체계 일관성**:
   - `practice_detail_id`와 JSON의 `problem_id`를 명확히 구분
   - 프론트엔드에서 두 ID를 모두 유지

3. **unique_together 제약**:
   - 같은 사용자가 같은 문제를 여러 번 제출하면 업데이트됨
   - 이력 관리가 필요하다면 별도 모델 고려

4. **점수 계산 로직**:
   - 현재 SubmitProblemView는 단순히 전달받은 `score`를 저장
   - 아키텍처 평가 결과에서 점수를 정확히 계산하여 전달 필요

---

## 🔗 관련 파일

### 백엔드
- `backend/core/models/Practice_model.py`: Practice, PracticeDetail 모델
- `backend/core/models/activity_model.py`: UserSolvedProblem 모델
- `backend/core/views/activity_view.py`: SubmitProblemView
- `backend/core/views/practice_view.py`: PracticeDetailListView (신규)
- `backend/core/urls.py`: API 라우팅

### 프론트엔드
- `frontend/src/data/architecture_advanced_gcp.json`: 문제 데이터
- `frontend/src/features/practice/architecture/SystemArchitecturePractice.vue`: 메인 컴포넌트
- `frontend/src/features/practice/architecture/services/architectureApiFastTest.js`: API 서비스
- `frontend/src/features/practice/architecture/composables/useEvaluation.js`: 평가 로직

### 스크립트
- `backend/scripts/load_architecture_problems.py`: JSON → DB 로딩 스크립트 (신규)

---

## ✅ 다음 작업

이 계획서를 기반으로 다음을 진행하세요:

1. **Phase 1** 부터 순차적으로 구현
2. 각 Phase의 체크포인트를 확인하며 진행
3. 문제 발생 시 해당 Phase로 돌아가서 디버깅
4. 최종 검증 체크리스트 완료 후 배포

---

**작성일**: 2026-02-12
**작성자**: Claude Code
**버전**: 1.0
