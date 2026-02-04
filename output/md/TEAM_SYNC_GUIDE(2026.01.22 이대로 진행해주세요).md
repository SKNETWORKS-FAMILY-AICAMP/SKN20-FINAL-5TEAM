# 📋 조원 코드 동기화 가이드 (2026-01-22 리팩토링 반영)

프로젝트 구조와 데이터베이스 스키마에 큰 변화가 있었습니다. 코드를 `git pull` 하신 후, 아래 절차에 따라 로컬 환경을 반드시 동기화해 주시기 바랍니다.

---

## 1. 데이터베이스 초기화 및 마이그레이션 (필수)

기존의 마이그레이션 파일이 하나로 통합(`0001_initial.py`)되고 PK 명칭이 대거 변경되었습니다. DB 충돌을 방지하기 위해 로컬 DB를 초기화하고 다시 마이그레이션하는 것을 권장합니다.

### 🛠 수행 명령어 (터미널)

1. **로컬 데이터베이스 볼륨 삭제 (데이터가 초기화되니 주의하세요)**
   ```bash
   docker-compose down -v
   ```

2. **Docker 컨테이너 다시 실행**
   ```bash
  docker-compose up -d --build
   ```

3. **마이그레이션 적용**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

---

## 2. 주요 변경 사항 요약

본인의 담당 소스 코드에서 아래 변경된 명칭을 참조하고 있는지 확인하고 수정해야 합니다.

### 🆔 PK(Primary Key) 명칭 통일
*   모든 모델의 고유 ID는 이제 `id`입니다.
*   **기존**: `user_id`, `common_id`, `board_id` 등
*   **변경**: `id` (예: `user.id`, `common.id`)

### 📢 모델 명칭 및 필드 변경
*   **게시판 모델**: `Post` -> **`Notice`** (공지사항 용도 명확화)
*   **공지사항 필드**:
    *   `board_title` -> **`title`**
    *   `board_contents` -> **`contents`**
*   **회원 상세 관계**: `UserDetail`의 외래키 필드명이 `user_id` -> **`user`**로 변경되었습니다. (객체 접근 시 `user_detail.user` 사용)

### 🏗️ 공통 필드 도입 (BaseModel 상속)
모든 모델이 `BaseModel`을 상속받습니다. 이제 자동 생성되는 아래 필드들을 공통으로 사용할 수 있습니다:
*   `create_id`, `update_id` (생성/수정자 ID)
*   `create_date`, `update_date` (생성/수정 일시)
*   `use_yn` (사용 여부, 기본값 'Y')

### 🗑️ 모델 추가 및 삭제
*   **추가**: 연습 및 테스트용 **`Practice`** 모델이 추가되었습니다. (`practice_model.py`)
*   **삭제**: 불용 모델(`Product`, `Order`, `Review`)이 제거되었습니다.

---

## 3. 향후 모델 수정 시 주의사항

모델을 새로 만들거나 수정할 때는 프로젝트 루트에 있는 **`model_modify.md`** 가이드를 먼저 확인해 주세요! (BaseModel 상속 및 마이그레이션 관리 방법이 설명되어 있습니다.)
