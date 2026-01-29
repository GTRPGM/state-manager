📜 TRPG 시스템 데이터베이스 구축 계획서 (Master Plan)

1. 파일 구조 및 명명 규칙

시스템은 정적 구조(Base)와 동적 로직(Logic)을 엄격히 분리하여 관리합니다.

- B_ (Base): 테이블 스키마, 인덱스, 기본 시간 갱신 트리거를 포함합니다.
- L_ (Logic): 세션 생성 시 Session 0 데이터를 복제하는 함수 및 초기화 트리거를 포함합니다.

1. 핵심 운영 원칙: Session 0 Deep Copy

- Session 0: 00000000-0000-0000-0000-000000000000 ID를 시스템 마스터 세션으로 정의합니다.
- Master Data: 작가가 작성한 시나리오 원본 데이터는 각 테이블에 session_id = '0...0'으로 저장됩니다.
- Auto-Instantiation: 신규 세션 INSERT 시, 트리거가 마스터 데이터를 조회하여 해당 세션 ID로 복사본을 자동 생성합니다.

1. 상세 구축 로드맵

Phase 1: 기반 구조 구축 (Base)

- B_scenario.sql & B_session.sql 실행
  - 모든 엔티티의 부모가 되는 시나리오와 세션 테이블을 먼저 생성합니다.
  - B_session.sql 내에서 시스템 세션(UUID 0) 레코드를 강제 삽입합니다.
- 엔티티 테이블 생성 (B_npc.sql, B_enemy.sql, B_item.sql 등)
  - 사용자 원본 구조를 유지하며 테이블만 생성합니다. (초기화 함수 미포함)

Phase 2: 복제 로직 주입 (Logic)

- 엔티티별 복제 함수 (L_*.sql) 등록
  - WHERE session_id = '000...0' AND scenario_id = NEW.scenario_id 로직을 가진 함수를 등록합니다.
- 세션 트리거 연결
  - session 테이블에 AFTER INSERT 트리거를 연결하여 세션 생성과 동시에 모든 데이터가 복제되도록 설정합니다.
  - 무한 루프 방지: WHEN (NEW.session_id <> '0...0') 조건을 반드시 적용합니다.

Phase 3: 데이터 수급 및 검증 - [완료]

- [x] 마스터 데이터 로드: 시나리오 원형 데이터를 session_id = '0...0'으로 입력 완료.
- [x] 기본 엔티티 복제 검증: 새 세션 생성 시 NPC, Enemy 자동 생성 확인.
- [x] 관계 데이터 복제 검증 (RDB): player_npc_relations 테이블 초기화 확인.
- [x] 관계 데이터 복제 검증 (Graph): Apache AGE 내 RELATION Edge 복제 확인.

1. 시나리오 주입 API (Scenario Injection API) - [완료]

목적: 작가나 관리자가 시나리오 메타데이터와 마스터 엔티티(NPC, Enemy 등)를 한 번의 API 호출로 시스템에 등록할 수 있도록 합니다.

기능:

- [x] 시나리오 기본 정보 등록 (Title, Description 등)
- [x] 마스터 NPC 데이터 등록 (Session 0)
- [x] 마스터 Enemy 데이터 등록 (Session 0)
- [x] 시나리오 관계 데이터(Graph) 등록 (Session 0)
- [x] 테스트 코드 작성 및 검증 (test_logic_integration.py)
