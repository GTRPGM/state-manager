# Graph-First(AGE) 전환 통합 계획안 (충돌 정리 + 요구조건 반영)

## 0. 고정 규칙(이 문서 전체에 강제)

- 인벤토리 모델은 반드시 아래로 간다.
  - (:Player)-[:HAS_INVENTORY {active, activated_turn, deactivated_turn}]->(:Inventory)
  - (:Inventory)-[:CONTAINS {quantity, active, activated_turn, deactivated_turn}]->(:Item)
- "모든 엣지"는 공통으로 activate/deactivate 속성을 가진다.
  - 최소: active:boolean, activated_turn:int, deactivated_turn:int|null
- "모든 엔티티(노드)"는 session_id를 가진다.
  - 모든 Cypher는 실행 전/중에 session_id로 필터링(파라미터 강제)
- Cypher는 1급 객체다.
  - Cypher 로딩/캐싱/실행/파라미터 바인딩/결과 파싱은 전용 모듈로 분리한다.
- 라우터는 Cypher 중심으로 재작성한다.
  - 반환 모델 변경은 추후 협의(지금은 바꾸는 걸 막지 않는다).
- 관계 테이블은 전부 제거하고 관계는 그래프로만 표현한다.
- 동기화 책임은 DB가 가진다.
  - SQL 테이블 INSERT/UPDATE/DELETE -> 트리거로 그래프 노드/속성 동기화
- npc, enemy, item은 3개 아이디를 가진다.
  - id: uuid, scenario: str, rule: int
  - 나머지 엔티티의 id는 uuid 단일키
  - (추가) 모든 노드는 session_id 필수

---

## 1. 목표 아키텍처

### 1.1 하이브리드 경계(정리)

- SQL(PostgreSQL 테이블)
  - 엔티티의 "식별/수명주기/정적 메타데이터"만 유지
  - 예: player, npc, enemy, item, inventory(필요시) 같은 마스터/인스턴스 테이블
- Graph(Apache AGE)
  - "관계/동적 상태"는 100% 그래프가 소스 오브 트루스(SOT)
  - 예: 인벤토리 포함/장착/활성, NPC 호감도, 적대관계, 소유/위치 등

### 1.2 그래프 스키마(최소)

#### 노드 라벨 및 키

- :Player { id: uuid, session_id: uuid, ... }
- :Inventory { id: uuid, session_id: uuid, ... }
- :Item { id: uuid, session_id: uuid, scenario: str, rule: int, ... }
- :NPC { id: uuid, session_id: uuid, scenario: str, rule: int, ... }
- :Enemy { id: uuid, session_id: uuid, scenario: str, rule: int, ... }
- (확장 가능) :Location, :Quest, :Faction 등은 id(uuid)+session_id

#### 엣지 타입(전부 active/activated/deactivated 포함)

- (:Player)-[:HAS_INVENTORY {active, activated_turn, deactivated_turn}]->(:Inventory)
- (:Inventory)-[:CONTAINS {quantity, active, activated_turn, deactivated_turn}]->(:Item)
- (:Player)-[:RELATION {affinity, relation_type, meta_json, active, activated_turn, deactivated_turn}]->(:NPC)
- (선택) (:Player)-[:HOSTILE {threat, ... +active fields}]->(:Enemy)

#### 세션 필터 규칙(절대 룰)

- 모든 MATCH는 최소한 아래를 만족해야 한다.
  - 노드: {session_id: $session_id}
  - 엣지: active = true (기본값), 필요 시 inactive 포함 옵션 제공
- session_id가 없는 쿼리는 "실행 불가"로 간주하고 런타임에서 차단한다(가드).

---

## 2. Phase A: Cypher 1급 객체화(전용 실행 레이어 신설)

> 목표: .cypher를 SQL처럼 취급하지 말고 "쿼리 리소스 + 준비(prepare) + 안전한 파라미터 바인딩 + 결과 매핑"까지 전부 전용 엔진으로 뽑는다.

### 2.1 신규/수정 파일

- (신규) src/state_db/graph/cypher_engine.py
  - run_cypher(name_or_path, params, \*, fetch="all|one|none")
  - 내부에서 session_id 강제 주입/검증
- (신규) src/state_db/graph/query_registry.py
  - .cypher 파일 로딩/캐싱(해시 기반)
  - statement name(prepare 이름) 생성/관리
- (신규) src/state_db/graph/result_mapper.py
  - AGE 반환(agtype) -> 파이썬 dict/primitive로 변환
  - 원칙: Cypher에서 RETURN을 "프로퍼티 단위"로 풀어서 agtype 의존 최소화
- (수정) src/state_db/infrastructure/query_executor.py
  - SQL 실행기는 유지하되, Cypher 실행은 위 graph/ 모듈로 위임한다(경계 분리)
  - load_queries는 .sql만 담당하거나, .cypher 등록은 registry로 넘긴다.

### 2.2 파라미터/준비(prepare) 표준

- 모든 .cypher는 $session_id를 포함해야 한다.
- 파라미터는 절대 문자열 치환으로 박지 않는다.
  - DB driver의 파라미터 바인딩 + AGE prepared statement 방식으로만 전달
- 커넥션 풀 환경 고려:
  - "커넥션 단위"로 prepared statement 존재 여부를 캐시한다.
  - `statement name = "cy\_" + sha1(query_text)[:16]` 같은 방식 추천

### 2.3 개발 규칙(팀 규약)

- .cypher 파일은 "도메인 단위"로 쪼갠다.
  - inventory/earn_item.cypher, inventory/use_item.cypher, relation/update_affinity.cypher ...
- .cypher 내부 RETURN은 최대한 스칼라로:
  - RETURN i.id, r.quantity, n.name ... 처럼 "필드 풀어서" 반환

---

## 3. Phase B: DB가 동기화 책임(트리거/초기화 정비)

> 목표: SQL 엔티티 row가 생기면 그래프 노드는 무조건 맞춰진다. 앱 레벨에서 동기화 로직 금지.

### 3.1 트리거로 그래프 노드 생성/업데이트 강제

- 대상 테이블(예시)
  - player, inventory, item, npc, enemy
- 이벤트
  - AFTER INSERT: 대응 노드 CREATE(없으면)
  - AFTER UPDATE: 그래프 노드 프로퍼티 UPDATE
  - AFTER DELETE(선택): soft-delete면 active=false로(노드 삭제는 신중)

### 3.2 세션 스코프 강제

- session 생성 시점에 아래가 보장돼야 한다.
  - session_id 발급
  - 필요한 엔티티 seed가 있다면 SQL insert -> 트리거로 그래프 생성
- 이 단계에서 "세션별 item 복제"가 필요하면:
  - SQL 복제 트리거가 그래프 노드에도 동일하게 반영되도록 수정

### 3.3 제거 대상(관계 테이블 전부)

- inventory 관계용 테이블(예: player_inventory, inventory_item 등) 제거
- 관계/호감도 테이블(예: player_npc_relations 등) 제거
- 관련 BASE/UPDATE SQL 쿼리 파일도 제거 또는 보관 폴더로 이동(deprecated)

---

## 4. Phase C: 도메인 Cypher 쿼리 구현(인벤토리/관계)

### 4.1 인벤토리: earn_item.cypher

- 입력: session_id, player_id(uuid), inventory_id(uuid, 없으면 생성은 SQL/트리거에서), item_key(3-ID), delta_qty, turn
- 로직(개념)
  - MATCH (p:Player {id:$player_id, session_id:$session_id})
  - MATCH (inv:Inventory {id:$inventory_id, session_id:$session_id})
  - MATCH (i:Item {id:$item_uuid, session_id:$session_id, scenario:$scenario, rule:$rule})
  - MERGE (p)-[h:HAS_INVENTORY]->(inv) SET h.active=true, h.activated_turn=coalesce(h.activated_turn,$turn)
  - MERGE (inv)-[c:CONTAINS]->(i)
    - ON CREATE: c.quantity=$delta_qty, c.active=true, c.activated_turn=$turn
    - ON MATCH: c.quantity=c.quantity+$delta_qty, c.active=true, c.deactivated_turn=null
  - RETURN c.quantity

### 4.2 인벤토리: use_item.cypher

- 입력: session_id, player_id, inventory_id, item_key(3-ID), use_qty, turn
- 로직(개념)
  - MATCH 경로: (p)-[h:HAS_INVENTORY {active:true}]->(inv)-[c:CONTAINS {active:true}]->(i)
  - c.quantity = c.quantity - $use_qty
  - if c.quantity <= 0:
    - c.active=false, c.deactivated_turn=$turn, c.quantity=0
  - RETURN c.quantity, c.active

### 4.3 관계/호감도: relation.cypher

- 입력: session_id, player_id, npc_key(3-ID), delta_affinity, relation_type, meta_json, turn
- 로직(개념)
  - MATCH (p:Player {id:$player_id, session_id:$session_id})
  - MATCH (n:NPC {id:$npc_uuid, session_id:$session_id, scenario:$scenario, rule:$rule})
  - MERGE (p)-[r:RELATION {relation_type:$relation_type}]->(n)
    - ON CREATE: r.affinity=$delta_affinity, r.active=true, r.activated_turn=$turn, r.meta_json=$meta_json
    - ON MATCH: r.affinity=r.affinity+$delta_affinity, r.active=true, r.deactivated_turn=null, r.meta_json=$meta_json
  - RETURN r.affinity, r.active

---

## 5. Phase D: Repository/Service 정리(관계는 그래프만)

### 5.1 Repository 수정 방향

- src/state_db/repositories/player.py
  - earn_item(): SQL 업데이트 삭제 -> cypher_engine.run_cypher("inventory/earn_item.cypher", params)
  - use_item(): SQL 업데이트 삭제 -> cypher_engine.run_cypher("inventory/use_item.cypher", params)
  - update_npc_affinity(): SQL 업데이트 삭제 -> cypher_engine.run_cypher("relation/relation.cypher", params)
- src/state_db/repositories/scenario.py
  - "시나리오 주입"은 SQL row 생성(정적/식별)까지만 하고,
  - 그래프 노드 생성/동기화는 트리거가 책임진다(앱에서 CREATE 금지).
  - 단, 시나리오 주입 시 "item/npc/enemy의 (scenario, rule) 매핑" 데이터는 SQL에 저장돼야 트리거가 정확히 노드에 반영 가능
- src/state_db/repositories/entity.py
  - 조회는 가능하면 그래프를 기준으로(특히 관계 포함 조회)

### 5.2 Service 레이어

- src/state_db/services/state_service.py
  - get_state_snapshot / get_session_context는 그래프 기반 조회 메서드로 이동
  - SQL JOIN 기반 스냅샷은 제거(또는 deprecated)

---

## 6. Phase E: Router를 Cypher 중심으로 재작성(통합 Context 조회)

### 6.1 라우터 변경

- 대상: src/state_db/routers/router_INQUIRY.py
- 목표: GM에게 전달할 get_session_context를 "단일(또는 소수) Cypher"로 뽑는다.

### 6.2 context.cypher(신규) 설계

- 입력: session_id, player_id, include_inactive(optional)
- 반환(예시: row 기반으로 평탄화)
  - inventory_items: item_uuid, scenario, rule, name, quantity, active
  - relations: npc_uuid, scenario, rule, name, affinity, relation_type, active
- 패턴(개념)
  - MATCH (p:Player {id:$player_id, session_id:$session_id})
  - OPTIONAL MATCH (p)-[h:HAS_INVENTORY]->(inv)-[c:CONTAINS]->(i:Item)
    - WHERE (h.active=true AND c.active=true) or include_inactive
  - OPTIONAL MATCH (p)-[r:RELATION]->(n:NPC)
    - WHERE r.active=true or include_inactive
  - RETURN ... (필드 단위로)

---

## 7. Phase F: 마이그레이션/정리(테이블 제거 + 데이터 이행)

### 7.1 1회성 마이그레이션(필요 시)

- 기존 세션 데이터가 이미 관계 테이블에 있다면:
  - migrate_inventory.cypher / migrate_relations.cypher를 만들어 한 번만 옮긴다.
  - 옮긴 뒤 관계 테이블 drop

### 7.2 제거 리스트(확정)

- Query/UPDATE/\* 관계 SQL 전부 제거 (earn_item.sql, use_item.sql, update_affinity.sql 등)
- 관계 테이블 생성용 BASE SQL 전부 제거
- Session_inventory.sql 같은 조회 JOIN 쿼리도 그래프 기반으로 교체

---

## 8. 작업 파일 리스트(최종)

### 8.1 신규

- src/state_db/graph/cypher_engine.py
- src/state_db/graph/query_registry.py
- src/state_db/graph/result_mapper.py
- src/state_db/Query/CYPHER/inventory/earn_item.cypher
- src/state_db/Query/CYPHER/inventory/use_item.cypher
- src/state_db/Query/CYPHER/relation/relation.cypher
- src/state_db/Query/CYPHER/inquiry/context.cypher

### 8.2 수정

- src/state_db/infrastructure/query_executor.py (SQL과 Cypher 실행 경계 분리)
- src/state_db/repositories/player.py
- src/state_db/repositories/scenario.py
- src/state_db/repositories/entity.py (조회가 관계를 그래프에서 읽도록)
- src/state_db/routers/router_INQUIRY.py
- (트리거) src/state_db/Query/BASE/L_graph.sql 또는 트리거 정의 파일들

### 8.3 삭제/Deprecated 이동

- src/state_db/Query/UPDATE/inventory/earn_item.sql
- src/state_db/Query/UPDATE/inventory/use_item.sql
- src/state_db/Query/UPDATE/relations/update_affinity.sql
- 관계 테이블 생성/조회용 BASE/INQUIRY SQL 전부

---

## 9. 검증 전략

- 목표: API 계약이 유지되는 범위에서 테스트 수정 최소화
- 필수 테스트 케이스
  - session_id 누락/불일치 시 Cypher 실행이 차단되는지
  - earn_item -> CONTAINS upsert가 정확한지(누적/활성화/비활성화)
  - use_item -> 0 이하에서 deactivate 처리되는지
  - update_npc_affinity -> 누적합 + active 상태 처리되는지
  - context.cypher가 한번에 inventory + relations를 뽑는지(필터/옵션 포함)

---

## 10. 운영 규칙(실수 방지용)

- "관계" 데이터는 SQL에 저장 금지(테이블 자체 없음)
- 그래프 쿼리에서 전체 노드 반환 금지(가능하면 필드 반환)
- 모든 쿼리는 $session_id를 강제하고, 기본은 active=true만 반환
- 동기화는 트리거만: 앱에서 그래프 노드 생성 로직을 두지 않는다
