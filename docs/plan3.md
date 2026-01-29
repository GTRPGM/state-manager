📄 SCHEMAS_PLAN.md
본 문서는 QUERY_STRUCTURE.md의 구조를 반영하여 schemas.py를 순차적으로 재구성하기 위한 로드맵입니다. 모든 단계는 한 번에 하나의 클래스(필드)씩 검토 및 확정하며 진행합니다.


1단계: 공통 믹스인 (Common Mixins)
여러 엔티티와 요청에서 반복되는 필드를 표준화하여 코드 중복을 방지합니다.

1-1. SessionContextMixin: session_id 등 세션 식별 정보

1-2. EntityBaseMixin: name, description, tags 등 기본 정보

1-3. StateMixin: numeric, boolean 등 JSONB 상태 데이터 구조



2단계: 엔티티 기반 스키마 (Entity Foundations)
BASE 테이블 정의와 INQUIRY 조회를 위한 핵심 엔티티 구조를 정의합니다.

2-1. PlayerBase: 플레이어 고유 속성

2-2. NPCBase: NPC 고유 속성 및 마스터 데이터 연결

2-3. EnemyBase: 적 개체 속성 및 전투 관련 필드

2-4. ItemBase: 아이템 명세 및 메타데이터



3단계: 시스템 로직 스키마 (System Logic)
L_ 파일의 트리거 및 UPDATE 카테고리의 동적 변화를 처리하기 위한 스키마입니다.

3-1. TurnRecord: record_state_change 로직을 위한 턴 이력 구조

3-2. PhaseTransition: 페이즈 전환 및 규칙 검증 데이터

3-3. LocationData: 위치 이동 및 세션 상태 업데이트 정보



4단계: 관계 및 시나리오 스키마 (Graph & Meta)
START_by_session의 Cypher 데이터와 시나리오 관리용 구조입니다.

4-1. RelationEdge: 엔티티 간의 관계(Edge) 및 호감도 정보

4-2. ScenarioMetadata: 시나리오 주입 및 전체 정보 관리



5단계: 관리 및 진단 스키마 (Manage & Debug)
MANAGE 및 DEBUG 카테고리 대응을 위한 운영용 스키마입니다.

5-1. SessionControl: 세션 생명주기(Pause/Resume/End) 제어

5-2. DebugDump: 시스템 정밀 진단 및 상태 덤프 구조