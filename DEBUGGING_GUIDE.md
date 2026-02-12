# Learning Analytics 디버깅 가이드

## 🔍 문제 진단 체크리스트

### 1. 레이더 차트가 안 나오는 경우

#### 원인 A: 문제 풀이 기록이 없음
```bash
# Django shell에서 확인
python manage.py shell
>>> from core.models import UserSolvedProblem
>>> UserSolvedProblem.objects.filter(user__email='your@email.com').count()
```

**해결:**
- Pseudo Practice 또는 Bug Hunt 문제를 최소 3개 이상 풀이

#### 원인 B: submitted_data가 비어있음
```python
>>> from core.models import UserSolvedProblem
>>> problem = UserSolvedProblem.objects.first()
>>> print(problem.submitted_data)  # None 또는 {} 면 메트릭 없음
```

**해결:**
- 문제 풀이 시 metrics 데이터가 제대로 저장되도록 수정

---

### 2. 동영상 추천이 안 나오는 경우

#### 원인 A: DB에 REFERENCE 데이터가 없음
```python
>>> from core.models import PracticeDetail
>>> PracticeDetail.objects.filter(detail_type='REFERENCE', is_active=True).count()
0  # ← 0이면 DB에 영상 자료 없음
```

**해결:**
- fixtures 로드 또는 REFERENCE 타입 PracticeDetail 생성

#### 원인 B: YouTube API 키가 없음
```python
# settings.py 확인
GOOGLE_API_KEY = None  # ← None이면 YouTube 검색 불가
```

**해결:**
```python
# config/settings.py
GOOGLE_API_KEY = 'YOUR_YOUTUBE_DATA_API_V3_KEY'
```

#### 원인 C: GPT가 recommended_video를 생성하지 않음
- 백엔드 콘솔 로그 확인:
```
DEBUG: GPT Report = {...}
```

---

### 3. 성장 추세가 안 나오는 경우

#### 원인: 문제를 3개 미만으로 풀었음
```python
>>> UserSolvedProblem.objects.filter(
...     user__email='your@email.com',
...     practice_detail__practice__title__iregex=r'pseudo|bug'
... ).count()
2  # ← 3개 미만이면 추세 계산 불가
```

**해결:**
- 같은 Practice를 3개 이상 풀이

---

## 🧪 테스트 순서

1. **브라우저 콘솔 확인** (F12)
   - API 응답 구조 확인
   - radar, recommended_video, growth_analysis 확인

2. **백엔드 콘솔 확인**
   - Worker 실행 로그 확인
   - GPT 응답 확인
   - YouTube 검색 결과 확인

3. **DB 데이터 확인**
   - 문제 풀이 기록
   - REFERENCE 데이터
   - submitted_data 메트릭

---

## 💡 빠른 해결책

### 레이더 차트 강제 표시 (테스트용)
```javascript
// LearningAnalytics.vue
const hasRadarData = computed(() => {
  return true;  // 임시로 true 반환
});
```

### 동영상 강제 표시 (테스트용)
```vue
<!-- v-if 조건 제거 -->
<section class="video-section">
  ...
</section>
```

---

## 📌 최종 체크

실제 운영 환경에서는:
1. ✅ fixtures에 REFERENCE 데이터 추가
2. ✅ YouTube API 키 설정
3. ✅ 문제 풀이 시 metrics 저장 확인
4. ✅ 최소 3개 이상 문제 풀이 유도
