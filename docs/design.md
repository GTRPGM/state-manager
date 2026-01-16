## 계획

1. GM 업무 구분

# GM의 역할

- 플레이어 입력/gm 입력으로 룰 엔진에 요청
- 룰엔진 상태 변경 내용을 시나리오에 맞춰 수정
- 상태 변경 적용
- 상태 변경 결과 전달
- 상태 변경 결과 요약 서술 전달

# 업무 종류
- [ ] 기반시스템 구축
     * rule engine & state DB 계약 정의 
     * play_log_DB 설계 

- [ ] 핵심로직 구현
     * GM 핵심 처리루프 구현 
     * Scenario DB 연계방식 확정

- [ ] 요약 및 서술화 
     * Description LLM 연결
     * Vector DB 활용정리 

==================================================

2. 업무별 설계 내역

- [ ] [state DB]
# State DB 및 파이프라인 설계 요약

## 1. State DB 설계 (Apache AGE)

### 1) 데이터 모델 (독립 저장 방식)
* **상태 정의(불변):** `(State) -[:CAN_TRANSITION_TO {condition_ref, probability}]-> (State)`
* **상태 인스턴스(가변):** `(Entity) -[:IN_STATE {session_id, since_turn, flags}]-> (State)`

### 2) 기술 스택 및 목적
* **엔진:** Apache AGE (PostgreSQL Extension)
* **언어:** Cypher + SQL Hybrid
* **목적:** 상태 구조 표현, 관계 조회, 현재 상태 스냅샷 확인
* **비목적:** 대규모 경로 최적화, 확률 계산, 정책 판단(Rule Evaluation)

### 3) 데이터 명세 및 제약
* **식별자:** `state_id`(PK), `session_id`(UUID), `state_name`, `state_type`(enum)
* **무결성 제약:** 동일 State 재진입 제한, 전이 Depth 제한, 확률 합(≤ 1) 검증

---

## 2. State DB 파이프라인 정의

### [1] External Pipeline (인터페이스 계층)
* **목표:** 외부 데이터를 정제하여 시스템 내부 표준 규격으로 변환
* **주요 기능:** * **Input Listener:** 유저/GM Action 수신
    * **Context Mapper:** Session ID 기반 캐릭터/시나리오 정보 매핑
    * **Preprocessing:** 자연어 입력을 정형 데이터로 가공 (Parsing)
* **사용 연산:** `Parse`

### [2] GM Orchestration Pipeline (비즈니스 계층)
* **목표:** 엔진 및 DB 간의 흐름 제어 및 상태 전환 의사결정
* **주요 기능:**
    * **Snapshot Fetcher:** 현재 `IN_STATE` 정보 조회
    * **Rule Engine Broker:** 현재 상태 + 입력을 전달하여 전이 판정 요청
    * **State Applier:** 확정된 결과를 Internal Pipeline에 적용 요청
    * **Event Dispatcher:** 변경 확정 시 Redis(Cache) 및 Scenario Writer 통보
* **사용 연산:** `Query`, `Request`, `Broadcast`

### [3] State DB Internal Pipeline (저장 및 무결성 계층)
* **목표:** DB 내부 무결성 검증 및 데이터 영속화
* **주요 기능:**
    * **Graph Schema Guard:** 정의되지 않은(Schema-off) 전이 발생 차단
    * **Integrity Checker:** 순환/폭주 방지 및 비즈니스 규칙 검사
    * **Transition Processor:** 기존 `IN_STATE` 삭제 및 신규 엣지 생성 (Atomic Update)
* **사용 연산:** `Validate`, `Update (Writing)`

---

## 3. 모듈별 연결 관계
* **GM:** 전체 파이프라인 제어 (조회 및 적용 주체)
* **Rule Engine:** GM의 요청에 따른 상태 전이 가능 여부 판단
* **Scenario Writer:** 확정된 상태 변화를 기반으로 서사 생성

