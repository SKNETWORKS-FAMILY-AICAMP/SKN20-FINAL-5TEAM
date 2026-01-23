업로드해주신 `component.md` 파일의 내용을 바탕으로, **면접 분석**이라는 목적에 최적화된 시스템 아키텍처 구성 요소를 다시 정리해 드립니다.

특히 질문하신 **검색 엔진**과 **모니터링/로깅**은 시스템의 완성도를 평가하는 핵심 지표이므로, 이를 포함하여 **[4가지 평가 기준]**에 맞게 구조화했습니다.

---

# 📄 시스템 아키텍처 컴포넌트 프리셋 (최종안)

이 프리셋은 특정 벤더(Vendor)에 종속되지 않고 시스템의 **역할(Role)**에 집중하여, 면접 시 설계 의도를 명확히 전달하는 데 목적을 둡니다.

## 1. 평가 기준 및 설계 원칙

* **Topic Suitability:** 면접관이 기술적 역량을 확인할 수 있는 필수 구성 요소 위주로 선정합니다.
* **Data Collection Possibility:** 각 컴포넌트의 선택 및 속성(Type, Tag)을 데이터화하여 사용자의 설계 수준을 분석합니다.
* **Topic Necessity:** 실제 서비스 운영 시 발생하는 문제(성능, 장애, 확장성)에 대한 대응 능력을 보여줍니다.
* **Expected Difficulties:** 구현 복잡도를 낮추기 위해 '추상화된 프리셋'을 제공하고 속성창에서 상세 설정을 하도록 구성합니다.

---

## 2. 레이어별 컴포넌트 그룹

### 그룹 A. 진입 및 연산 (Compute & Entry)

* **User/Client:** 시스템 접속 주체 (Mobile, Web, IoT).
* **Load Balancer:** 트래픽 분산 및 가용성 확보 (L4/L7, ELB 등).
* **API Gateway:** 라우팅, 인증/인가, 속도 제한(Throttling).
* **Compute Service:** 비즈니스 로직 실행 단위 (Server, Container, Lambda).

### 그룹 B. 저장소 및 검색 (Storage & Search)

* **Relational DB (RDBMS):** 트랜잭션과 데이터 정합성 관리 (MySQL, PostgreSQL).
* **NoSQL DB:** 비정형 데이터 및 수평 확장성 (MongoDB, DynamoDB).
* **In-Memory Cache:** 읽기 성능 최적화 (Redis, Memcached).
* **Search Engine:** **(추가)** 대용량 텍스트 검색 및 분석 (Elasticsearch, Meilisearch).
* **Object Storage:** 파일 및 정적 에셋 저장 (S3).

### 그룹 C. 메시징 및 비동기 (Messaging)

* **Message Broker:** 시스템 간 결합도 완화 및 비동기 처리 (Kafka, RabbitMQ).
* **Event Bus:** 이벤트 기반 아키텍처 구현 (EventBridge, SNS).

### 그룹 D. 운영 및 관제 (Observability) - **신규 추가**

* **Monitoring:** 시스템 메트릭 수집 및 알람 (Prometheus, Grafana).
* **Logging:** 로그 수집 및 문제 추적 (ELK Stack, CloudWatch).
* **CI/CD:** 배포 자동화 및 버전 관리 (GitHub Actions, Jenkins).

---
