# 구현 계획: User ID 매핑 기반 세션 관리

## 개요
Session 테이블에 `user_id` 컬럼을 추가하여 외부에서 전달받은 사용자 식별자를 세션에 매핑합니다.
별도의 User 테이블 없이 단순 매핑만 수행하며, user_id로 연결된 활성 세션 조회 기능을 제공합니다.

---

## 핵심 원칙

| 항목 | 설명 |
|------|------|
| 독립적 session_id | 모든 데이터는 session_id를 중심으로 관리 |
| Optional user_id | FK 제약조건 없이 단순 정수(INT) 컬럼으로 저장 |
| 생명주기 위임 | user_id 관리는 외부 시스템 책임, StateManager는 매핑만 담당 |
| 자연 삭제 | 세션 삭제 시 user_id 정보도 함께 삭제됨 |

---

## Phase 1: DB 스키마 수정

### 1.1 session 테이블에 user_id 컬럼 추가 --complete

**경로**: `src/state_db/Query/BASE/B_session.sql`

```sql
-- session 테이블에 user_id 컬럼 추가
-- FK 제약조건 없음 (외부 시스템에서 관리)
ALTER TABLE session ADD COLUMN IF NOT EXISTS user_id INTEGER DEFAULT NULL;

-- user_id 인덱스 추가 (조회 성능)
CREATE INDEX IF NOT EXISTS idx_session_user_id ON session(user_id);
```

### 1.2 마이그레이션 SQL 파일 생성 --complete

**경로**: `src/state_db/Query/MIGRATE/add_user_id_to_session.sql` (신규)

```sql
-- 마이그레이션: session 테이블에 user_id 컬럼 추가
-- 실행 시점: 기존 DB에 적용 시

ALTER TABLE session ADD COLUMN IF NOT EXISTS user_id INTEGER DEFAULT NULL;
CREATE INDEX IF NOT EXISTS idx_session_user_id ON session(user_id);

COMMENT ON COLUMN session.user_id IS '외부 시스템의 사용자 식별자 (Optional, FK 없음, INTEGER)';
```

---

## Phase 2: SQL 함수 수정

### 2.1 create_session 함수 수정 --complete

**경로**: `src/state_db/Query/FIRST/session.sql`

```sql
-- create_session 함수에 user_id 파라미터 추가
CREATE OR REPLACE FUNCTION create_session(
    p_scenario_id UUID,
    p_current_act INTEGER DEFAULT 1,
    p_current_sequence INTEGER DEFAULT 1,
    p_location TEXT DEFAULT NULL,
    p_user_id INTEGER DEFAULT NULL  -- 신규 파라미터
)
RETURNS UUID AS $$
DECLARE
    new_session_id UUID;
BEGIN
    INSERT INTO session (
        scenario_id,
        current_act,
        current_sequence,
        location,
        status,
        current_phase,
        user_id  -- 신규 컬럼
    )
    VALUES (
        p_scenario_id,
        p_current_act,
        p_current_sequence,
        p_location,
        'active',
        'dialogue',
        p_user_id  -- 신규 값
    )
    RETURNING session_id INTO new_session_id;

    RETURN new_session_id;
END;
$$ LANGUAGE plpgsql;
```

### 2.2 user_id 업데이트 함수 추가 --complete

**경로**: `src/state_db/Query/MANAGE/session/update_user_id.sql` (신규)

```sql
-- session에 user_id 매핑/업데이트
UPDATE session
SET user_id = $2
WHERE session_id = $1::uuid
RETURNING session_id, user_id;
```

---

## Phase 3: 조회 SQL 수정/추가

### 3.1 Session_active.sql 수정 --complete

**경로**: `src/state_db/Query/INQUIRY/session/Session_active.sql`

```sql
SELECT
    s.session_id,
    s.scenario_id,
    s.user_id,           -- 추가
    p.player_id,
    s.current_act,
    s.current_sequence,
    s.current_act_id,
    s.current_sequence_id,
    s.current_phase,
    s.current_turn,
    s.location,
    s.status,
    s.started_at,
    s.ended_at,
    s.created_at,
    s.updated_at
FROM session s
LEFT JOIN player p ON s.session_id = p.session_id
WHERE s.status = 'active'
ORDER BY s.started_at DESC;
```

### 3.2 Session_by_user.sql 추가 (신규) --complete

**경로**: `src/state_db/Query/INQUIRY/session/Session_by_user.sql`

```sql
-- user_id로 활성 세션 조회
SELECT
    s.session_id,
    s.scenario_id,
    s.user_id,
    p.player_id,
    s.current_act,
    s.current_sequence,
    s.current_act_id,
    s.current_sequence_id,
    s.current_phase,
    s.current_turn,
    s.location,
    s.status,
    s.started_at,
    s.ended_at,
    s.created_at,
    s.updated_at
FROM session s
LEFT JOIN player p ON s.session_id = p.session_id
WHERE s.user_id = $1
  AND s.status = 'active'
ORDER BY s.started_at DESC;
```

### 3.3 기타 Session 조회 SQL 수정 --complete

다음 파일들에 `s.user_id` 컬럼 추가:
- `Session_show.sql`
- `Session_all.sql`
- `Session_paused.sql`
- `Session_ended.sql`

---

## Phase 4: Python 모델 수정

### 4.1 SessionInfo 모델 수정 --complete

**경로**: `src/state_db/models/session.py`

```python
class SessionInfo(BaseModel):
    session_id: Union[str, UUID]
    scenario_id: Union[str, UUID]
    user_id: Optional[int] = None  # 신규 필드 (INTEGER)
    player_id: Optional[Union[str, UUID]] = None
    # ... 기존 필드 유지
```

---

## Phase 5: Repository 수정

### 5.1 SessionRepository 수정 --complete

**경로**: `src/state_db/repositories/session.py`

```python
class SessionRepository(BaseRepository):

    async def start(
        self,
        scenario_id: str,
        act: int,
        sequence: int,
        location: str,
        user_id: Optional[int] = None  # 신규 파라미터 (INTEGER)
    ) -> SessionInfo:
        # execute_sql_function에 user_id 추가
        result = await execute_sql_function(
            "create_session",
            [scenario_uuid, act, sequence, location, user_id]
        )
        # ...

    async def update_user_id(self, session_id: str, user_id: int) -> dict:
        """세션에 user_id 매핑"""
        sql_path = self.query_dir / "MANAGE" / "session" / "update_user_id.sql"
        result = await run_sql_query(sql_path, [session_id, user_id])
        if result:
            return {"session_id": session_id, "user_id": user_id}
        raise HTTPException(status_code=404, detail="Session not found")

    async def get_sessions_by_user(self, user_id: int) -> List[SessionInfo]:
        """user_id로 활성 세션 조회"""
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_by_user.sql"
        results = await run_sql_query(sql_path, [user_id])
        return [SessionInfo.model_validate(row) for row in results]
```

---

## Phase 6: API 엔드포인트 수정/추가

### 6.1 세션 생성 API 수정 --complete

**경로**: `src/state_db/routers/router_START.py`, `src/state_db/schemas/management.py`

```python
class SessionStartRequest(BaseModel):
    scenario_id: str
    act: int = 1
    sequence: int = 1
    location: str = ""
    user_id: Optional[int] = None  # 신규 필드 (INTEGER)

@router.post("/session/start")
async def start_session(request: SessionStartRequest):
    return await session_repo.start(
        scenario_id=request.scenario_id,
        act=request.act,
        sequence=request.sequence,
        location=request.location,
        user_id=request.user_id  # 신규
    )
```

### 6.2 user_id 매핑 API 추가 --complete

```python
@router.patch("/session/{session_id}/user")
async def update_session_user(session_id: str, user_id: int):
    """기존 세션에 user_id 매핑"""
    return await session_repo.update_user_id(session_id, user_id)
```

### 6.3 user_id로 세션 조회 API 추가 --complete

```python
@router.get("/sessions/user/{user_id}")
async def get_sessions_by_user(user_id: int) -> List[SessionInfo]:
    """user_id에 연결된 활성 세션 목록 조회"""
    return await session_repo.get_sessions_by_user(user_id)
```

---

## 수정 파일 목록

| 작업 | 파일 경로 |
|------|----------|
| 수정 | `src/state_db/Query/BASE/B_session.sql` |
| 수정 | `src/state_db/Query/FIRST/session.sql` |
| 수정 | `src/state_db/Query/INQUIRY/session/Session_active.sql` |
| 수정 | `src/state_db/Query/INQUIRY/session/Session_show.sql` |
| 수정 | `src/state_db/Query/INQUIRY/session/Session_all.sql` |
| 수정 | `src/state_db/Query/INQUIRY/session/Session_paused.sql` |
| 수정 | `src/state_db/Query/INQUIRY/session/Session_ended.sql` |
| 수정 | `src/state_db/models/session.py` |
| 수정 | `src/state_db/repositories/session.py` |
| 수정 | `src/state_db/routers/session.py` (또는 해당 라우터) |
| 생성 | `src/state_db/Query/MIGRATE/add_user_id_to_session.sql` |
| 생성 | `src/state_db/Query/MANAGE/session/update_user_id.sql` |
| 생성 | `src/state_db/Query/INQUIRY/session/Session_by_user.sql` |

---

## 데이터 흐름 요약

```
┌─────────────────────────────────────────────────────────────┐
│                         GM (외부)                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  POST /session/start                                        │
│  { scenario_id, act, sequence, location, user_id? }         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  session 테이블                                              │
│  ┌──────────────┬──────────────┬──────────────┐            │
│  │ session_id   │ scenario_id  │ user_id      │ ...        │
│  │ (PK)         │ (FK)         │ (Optional)   │            │
│  └──────────────┴──────────────┴──────────────┘            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  GET /session/user/{user_id}                                │
│  → 해당 user_id에 매핑된 활성 세션 목록 반환                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 검증 방법

### 1. 마이그레이션 실행
```bash
psql -d your_database -f src/state_db/Query/MIGRATE/add_user_id_to_session.sql
```

### 2. 세션 생성 테스트 (user_id 포함)
```bash
curl -X POST http://localhost:8030/session/start \
  -H "Content-Type: application/json" \
  -d '{"scenario_id": "uuid-here", "user_id": 12345}'
```

### 3. user_id로 세션 조회 테스트
```bash
curl http://localhost:8030/session/user/12345
```

### 4. 기존 테스트 통과 확인
```bash
pytest tests/ -v
```

---

## 구현 순서

1. DB 스키마 수정 (B_session.sql + 마이그레이션 SQL)
2. SQL 함수 수정 (create_session, Session 조회 쿼리들)
3. 신규 SQL 파일 생성 (update_user_id.sql, Session_by_user.sql)
4. Python 모델 수정 (SessionInfo)
5. Repository 수정 (SessionRepository)
6. API 엔드포인트 수정/추가
7. 테스트 실행 및 검증
