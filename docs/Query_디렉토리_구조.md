# Query 폴더 구조 및 설명

## 📁 디렉토리 구조 개요

```
Query/
├── FIRST/                        # 테이블 생성 DDL (초기 DB 구성)
├── START_by_session/             # 세션 시작 시 실행되는 초기화 쿼리
├── INQUIRY/                      # 조회(SELECT) 쿼리 모음
├── TRACE/                        # 실시간 추적 및 히스토리 조회
├── UPDATE/                       # 상태 변경(UPDATE/INSERT) 쿼리
│   └── phase/                    # Phase별 행동 처리 트랜잭션
├── MANAGE/                       # 내부 관리 쿼리 (세션, phase, turn, act 등)
│   ├── session/                  # 세션 생명주기 관리
│   ├── phase/                    # Phase 전환 및 검증
│   ├── turn/                     # Turn 진행 관리
│   ├── act/                      # Act 관리
│   ├── sequence/                 # Sequence 관리
│   ├── location/                 # 위치 관리
│   ├── enemy/                    # Enemy 생성/제거
│   └── npc/                      # NPC 생성/제거
└── DEBUG/                        # 디버깅 및 통계 쿼리
```

---

## 📂 각 폴더 상세 설명


### **1️⃣ FIRST/** - 테이블 생성 (DDL)
```
목적: 데이터베이스 초기 구성 (테이블, 트리거, 함수 생성)
실행 시점: DB 최초 설정 시 한 번만 실행
파일 형식: .sql (DDL)

주요 파일:
├── session.sql                   # 세션 테이블 + Phase/Turn 개념 정의
├── player.sql                    # 플레이어 엔티티 테이블
├── npc.sql                       # NPC 엔티티 테이블
├── enemy.sql                     # Enemy 엔티티 테이블
├── item.sql                      # 아이템 마스터 데이터 테이블
├── inventory.sql                 # 인벤토리 테이블
├── player_inventory.sql          # 플레이어-아이템 관계 테이블
├── player_npc_relations.sql      # 플레이어-NPC 호감도 테이블
├── scenario.sql                  # 시나리오 메타데이터 테이블
├── phase_history.sql             # Phase 전환 히스토리 테이블
└── turn_history.sql              # Turn 히스토리 테이블

특징:
  - ENUM 타입 정의 (phase_type, session_status 등)
  - 트리거 함수 (updated_at 자동 갱신 등)
  - 제약조건 및 인덱스 설정
  - JSONB 필드 활용 (state, meta 등)
```

---

### **2️⃣ START_by_session/** - 세션 초기화
```
목적: 새 게임 세션 시작 시 필요한 데이터 생성
실행 시점: session_start() 호출 시
파일 형식: .sql (INSERT), .cypher (그래프)

주요 파일:
├── C_session.sql                 # 세션 생성
├── N_player.sql                  # 플레이어 생성
├── N_npc.sql                     # NPC 생성
├── N_enemy.sql                   # 초기 적 생성
├── E_player_inventory.sql        # 플레이어 인벤토리 초기화
├── earn_item.cypher              # 아이템 획득 그래프 (참조용)
├── player_inventory.cypher       # 인벤토리 그래프 (참조용)
├── relation.cypher               # 관계 그래프 (참조용)
└── used_item.cypher              # 아이템 사용 그래프 (참조용)

명명 규칙:
  - C_* : Create (생성)
  - N_* : Node (노드 생성)
  - E_* : Edge (엣지 생성)

특징:
  - .cypher 파일은 Apache AGE 그래프 쿼리 참조/문서화용
  - 실제 실행은 query.py에서 파일 읽어서 run_cypher_query()에 전달
```

---

### **3️⃣ INQUIRY/** - 조회 쿼리
```
목적: 데이터 조회 (SELECT)
실행 시점: 상태 확인 필요 시 (API GET 요청)
파일 형식: .sql (SELECT)

주요 파일:

[세션 조회]
├── Session_all.sql               # 세션 전체 정보
├── Session_active.sql            # 활성 세션 목록
├── Session_paused.sql            # 일시정지 세션 목록
├── Session_ended.sql             # 종료 세션 목록
├── Session_show.sql              # 세션 상세 정보
├── Session_phase.sql             # 현재 Phase 정보
├── Session_turn.sql              # 현재 Turn 정보
├── Session_player.sql            # 세션의 플레이어 정보
├── Session_inventory.sql         # 세션 인벤토리
├── Session_npc.sql               # 세션 NPC 목록
└── Session_enemy.sql             # 세션 Enemy 목록

[플레이어 조회]
├── Player_stats.sql              # 플레이어 상세 스탯
└── Npc_relations.sql             # 플레이어-NPC 호감도

[진행 상황 조회]
├── Act_now.sql                   # 현재 Act
├── Sequence_now.sql              # 현재 Sequence
└── Location_now.sql              # 현재 위치

명명 규칙:
  - Session_* : 세션 관련 조회
  - Player_* : 플레이어 관련 조회
  - *_now : 현재 상태 조회

query.py 함수:
  - get_session_inventory()
  - get_session_npcs()
  - get_session_enemies()
  - get_player_stats()
  - get_npc_relations()
```

---

### **4️⃣ TRACE/** - 히스토리 추적
```
목적: 실시간 변동 추적 및 히스토리 조회
실행 시점: 히스토리 분석 필요 시
파일 형식: .sql (SELECT + 복잡한 분석 쿼리)

주요 파일:
├── phase_tracing.sql             # Phase 전환 히스토리 조회 (700줄+)
└── turn_tracing.sql              # Turn 히스토리 조회 (900줄+)

내용:
  - Phase/Turn별 전환 이력
  - 통계 및 분석 쿼리
  - 소요 시간 계산
  - 패턴 분석
  - 리플레이 기능
  - 이상 탐지

특징:
  - 매우 상세한 DML 쿼리 모음 (작업영역별 주석 구분)
  - WITH 절, Window Function 활용
  - JSONB 집계 및 분석
```

---

### **5️⃣ UPDATE/** - 상태 업데이트
```
목적: 게임 상태 변경 (HP, 아이템, 호감도 등)
실행 시점: 게임 로직 실행 시 (API PUT/POST 요청)
파일 형식: .sql (UPDATE/INSERT)

주요 파일:

[플레이어 상태]
├── update_player_hp.sql          # 플레이어 HP 변경
├── update_player_stats.sql       # 플레이어 스탯 변경 (범용)
└── damaged.sql                   # 피해 처리 (구버전)

[NPC 상태]
└── update_npc_affinity.sql       # NPC 호감도 변경

[Enemy 상태]
├── update_enemy_hp.sql           # 적 HP 변경
└── defeated_enemy.sql            # 적 처치 처리

[아이템]
├── earn_item.sql                 # 아이템 획득
└── use_item.sql                  # 아이템 사용

[위치]
└── update_location.sql           # 위치 변경

[Phase별 트랜잭션]
└── phase/
    ├── combat_phase.sql          # 전투 행동 처리
    ├── exploration_phase.sql     # 탐색 행동 처리
    ├── dialogue_phase.sql        # 대화 행동 처리
    └── rest_phase.sql            # 휴식 행동 처리

query.py 함수:
  - update_player_hp()
  - update_player_stats()
  - update_npc_affinity()
  - update_enemy_hp()
  - defeat_enemy()
  - update_location()

특징:
  - JSONB 업데이트 패턴 사용
  - UPSERT 패턴 (INSERT ... ON CONFLICT)
  - Phase별 트랜잭션은 BEGIN/COMMIT 포함
```

---

### **6️⃣ MANAGE/** - 내부 관리
```
목적: 메타 관리 (세션, Phase, Turn, Act, Sequence 등)
실행 시점: GM 명령 또는 시스템 제어
파일 형식: .sql (UPDATE/DELETE)

구조:

[세션 생명주기]
└── session/
    ├── pause_session.sql         # 세션 일시정지
    ├── paused_check.sql          # 일시정지 확인
    ├── resume_session.sql        # 세션 재개
    └── end_session.sql           # 세션 종료

[Phase 관리]
└── phase/
    ├── change_phase.sql          # Phase 전환
    ├── phase_check.sql           # Phase 확인
    └── is_action_allowed.sql     # 행동 허용 검증

[Turn 관리]
└── turn/
    ├── add_turn.sql              # Turn 증가
    └── turn_changed.sql          # Turn 변경 확인

[Act 관리]
└── act/
    ├── select_act.sql            # Act 직접 지정
    ├── add_act.sql               # Act 증가
    ├── back_act.sql              # Act 롤백
    └── act_check.sql             # Act 확인

[Sequence 관리]
└── sequence/
    ├── select_sequence.sql       # Sequence 직접 지정
    ├── add_sequence.sql          # Sequence 증가
    ├── back_sequence.sql         # Sequence 롤백
    └── limit_sequence.sql        # Sequence 제한 확인

[위치 관리]
└── location/
    └── location_change.sql       # 위치 변경 (UPDATE로 이동 권장)

[엔티티 관리]
└── enemy/
    ├── spawn_enemy.sql           # 적 동적 생성
    └── remove_enemy.sql          # 적 제거
└── npc/
    ├── spawn_npc.sql             # NPC 동적 생성
    └── remove_npc.sql            # NPC 제거

query.py 함수:
  - spawn_enemy()
  - remove_enemy()
  - spawn_npc()
  - remove_npc()

특징:
  - GM 또는 시스템 제어용
  - RuleEngine과 연동
  - 상태 전환 검증 포함
```

---

### **7️⃣ DEBUG/** - 디버깅 및 통계
```
목적: 디버깅, 통계, 히스토리 분석
실행 시점: 개발/테스트 시 또는 데이터 분석 필요 시
파일 형식: .sql (복합 쿼리)

주요 파일:
├── concept.sql                   # 종합 개념 쿼리 모음 (600줄+)
├── A_phase.sql                   # Phase 분석
├── D_turn.sql                    # Turn 디버깅
├── H_Session_phase.sql           # 세션 Phase 히스토리
└── H_Session_turn.sql            # 세션 Turn 히스토리

내용:
  - 전체 상태 덤프
  - 데이터 무결성 검증
  - 통계 및 분석
  - 테스트 데이터 생성
  - 데이터 정리

명명 규칙:
  - A_* : Analysis (분석)
  - D_* : Debug (디버깅)
  - H_* : History (히스토리)

특징:
  - 복잡한 JOIN 및 집계 쿼리
  - 개발/테스트 환경용
  - 프로덕션에서는 신중히 사용
```

---

## 🔄 데이터 흐름

### 1. **세션 시작**
```
FIRST/ (테이블 생성) → START_by_session/ (초기 데이터 생성)
```

### 2. **게임 플레이**
```
INQUIRY/ (상태 조회)
  ↓
RuleEngine 판정
  ↓
UPDATE/ (상태 변경) + MANAGE/ (Phase/Turn 관리)
  ↓
TRACE/ (히스토리 기록)
```

### 3. **디버깅/분석**
```
DEBUG/ (통계 및 분석) ← TRACE/ (히스토리 데이터)
```

---

## 📊 파일 명명 규칙 요약

| 접두사 | 의미 | 예시 | 폴더 |
|--------|------|------|------|
| `C_*` | Create | C_session.sql | START_by_session/ |
| `N_*` | Node | N_player.sql | START_by_session/ |
| `E_*` | Edge | E_player_inventory.sql | START_by_session/ |
| `Session_*` | 세션 관련 | Session_all.sql | INQUIRY/ |
| `Player_*` | 플레이어 관련 | Player_stats.sql | INQUIRY/ |
| `*_now` | 현재 상태 | Act_now.sql | INQUIRY/ |
| `update_*` | 업데이트 | update_player_hp.sql | UPDATE/ |
| `A_*` | Analysis | A_phase.sql | DEBUG/ |
| `D_*` | Debug | D_turn.sql | DEBUG/ |
| `H_*` | History | H_Session_turn.sql | DEBUG/ |

---

## 🔧 query.py 함수 매핑

### 조회 함수
```python
# 인벤토리
get_session_inventory(session_id)              → INQUIRY/Session_inventory.sql

# NPC
get_session_npcs(session_id)                   → INQUIRY/Session_npc.sql
get_npc_relations(player_id)                   → INQUIRY/Npc_relations.sql

# Enemy
get_session_enemies(session_id, active_only)   → INQUIRY/Session_enemy.sql

# 플레이어
get_player_stats(player_id)                    → INQUIRY/Player_stats.sql
get_player_state(player_id)                    → 여러 쿼리 조합
```

### 업데이트 함수
```python
# 플레이어
update_player_hp(player_id, session_id, hp_change, reason)
  → UPDATE/update_player_hp.sql

update_player_stats(player_id, session_id, stat_changes)
  → UPDATE/update_player_stats.sql

# NPC
update_npc_affinity(player_id, npc_id, affinity_change)
  → UPDATE/update_npc_affinity.sql

# Enemy
update_enemy_hp(enemy_instance_id, session_id, hp_change)
  → UPDATE/update_enemy_hp.sql

defeat_enemy(enemy_instance_id, session_id)
  → UPDATE/defeated_enemy.sql

# 위치
update_location(session_id, new_location)
  → UPDATE/update_location.sql
```

### 관리 함수
```python
# Enemy
spawn_enemy(session_id, enemy_data)           → MANAGE/enemy/spawn_enemy.sql
remove_enemy(enemy_instance_id, session_id)   → MANAGE/enemy/remove_enemy.sql

# NPC
spawn_npc(session_id, npc_data)               → MANAGE/npc/spawn_npc.sql
remove_npc(npc_instance_id, session_id)       → MANAGE/npc/remove_npc.sql
```

---

## 💡 사용 가이드

### 1. **새 프로젝트 시작**
```sql
-- 1단계: FIRST/ 폴더의 모든 DDL 실행
psql -U postgres -d state_db -f FIRST/session.sql
psql -U postgres -d state_db -f FIRST/player.sql
-- ... (모든 테이블 생성)

-- 2단계: 세션 시작
-- query.py의 session_start() 함수 호출
```

### 2. **게임 플레이 흐름**
```python
# 1. 세션 생성
session = await session_start(scenario_id, player_data)

# 2. 상태 조회
inventory = await get_session_inventory(session_id)
enemies = await get_session_enemies(session_id)

# 3. 행동 처리 (예: 전투)
await update_player_hp(player_id, session_id, -10, "combat")
await update_enemy_hp(enemy_id, session_id, -20)

# 4. 엔티티 관리 (예: 적 생성)
new_enemy = await spawn_enemy(session_id, enemy_data)
```

### 3. **디버깅**
```sql
-- 세션 전체 상태 확인
\i DEBUG/concept.sql

-- Phase 히스토리 확인
\i TRACE/phase_tracing.sql
```

---

## ⚠️ 주의사항

### 1. **파일 형식**
- `.sql`: PostgreSQL 쿼리 (직접 실행 가능)
- `.cypher`: Apache AGE 그래프 쿼리 (참조/문서화용, 실행 시 query.py 거쳐야 함)
- `.py`: Python 함수 인터페이스

### 2. **트랜잭션**
- `UPDATE/phase/` 폴더의 쿼리는 `BEGIN/COMMIT` 포함
- 나머지 쿼리는 query.py에서 트랜잭션 관리

### 3. **경로**
- query.py에서 쿼리 파일 로드 시 상대 경로 사용
- `Path(__file__).parent / "Query/INQUIRY/Session_all.sql"`

### 4. **JSONB 필드**
- `state`: 플레이어/NPC/Enemy의 동적 스탯
- `meta`: 확장 메타데이터
- jsonb_set() 함수로 업데이트

---

## 📈 향후 확장 계획

1. **INQUIRY/** - 추가 조회 쿼리
   - Session_rewards.sql (세션 보상 조회)
   - Session_quests.sql (퀘스트 진행 조회)

2. **UPDATE/** - 추가 업데이트 쿼리
   - update_quest.sql (퀘스트 상태 변경)
   - update_rewards.sql (보상 지급)

3. **MANAGE/snapshot/** - 스냅샷 관리
   - save_snapshot.sql (수동 스냅샷 저장)
   - load_snapshot.sql (스냅샷 복원)

4. **DEBUG/** - 추가 디버깅 쿼리
   - validate_integrity.sql (데이터 무결성 검증)
   - performance_analysis.sql (성능 분석)

---

## 📞 문의 및 참고

- **프로젝트**: Interactive LLM TRPG State Manager
- **역할**: State Manager (상위: GM, 협력: RuleEngine, Scenario Writer)
- **아키텍처**:
  - Input parsing: FE-BE-GM (LangGraph 사용)
  - Orchestration: 외부 연계 pipeline
  - Internal runtime: 실시간 상태 유지

---

**마지막 업데이트**: 2026-01-25
