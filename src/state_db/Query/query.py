# query.py - TRPG 상태 DB 쿼리 관리

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

import asyncpg
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict

from state_db.configs.setting import AGE_GRAPH_NAME, DB_CONFIG

# ====================================================================
# Type Definitions (Pydantic Models)
# ====================================================================


class SessionInfo(BaseModel):
    session_id: str
    scenario_id: str
    player_id: str
    current_act: int
    current_sequence: int
    location: str
    status: str
    created_at: Any  # datetime
    updated_at: Any  # datetime
    model_config = ConfigDict(from_attributes=True)


class InventoryItem(BaseModel):
    player_id: str
    item_id: int
    quantity: int
    acquired_at: Any  # datetime
    model_config = ConfigDict(from_attributes=True)


class NPCInfo(BaseModel):
    npc_id: str
    name: str
    description: str
    hp: int
    tags: List[str]
    model_config = ConfigDict(from_attributes=True)


class NPCRelation(BaseModel):
    npc_id: str
    npc_name: str
    affinity_score: int
    model_config = ConfigDict(from_attributes=True)


class EnemyInfo(BaseModel):
    enemy_instance_id: str
    enemy_id: int
    name: str
    hp: int
    current_hp: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class PlayerStateNumeric(BaseModel):
    HP: Optional[int] = None
    MP: Optional[int] = None
    gold: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class PlayerState(BaseModel):
    numeric: PlayerStateNumeric
    boolean: Dict[str, bool]
    model_config = ConfigDict(from_attributes=True)


class PlayerStats(BaseModel):
    player_id: str
    name: str
    state: PlayerState
    relations: List[Any]
    tags: List[str]
    model_config = ConfigDict(from_attributes=True)


class PlayerStateResponse(BaseModel):
    hp: int
    gold: int
    items: List[int]
    model_config = ConfigDict(from_attributes=True)


class FullPlayerState(BaseModel):
    player: PlayerStateResponse
    player_npc_relations: List[NPCRelation]
    model_config = ConfigDict(from_attributes=True)


class PlayerHPUpdateResult(BaseModel):
    player_id: str
    name: str
    current_hp: int
    max_hp: int
    hp_change: int
    model_config = ConfigDict(from_attributes=True)


class NPCAffinityUpdateResult(BaseModel):
    player_id: str
    npc_id: str
    new_affinity: int
    model_config = ConfigDict(from_attributes=True)


class EnemyHPUpdateResult(BaseModel):
    enemy_instance_id: str
    current_hp: int
    is_defeated: bool
    model_config = ConfigDict(from_attributes=True)


class DefeatEnemyResult(BaseModel):
    status: str
    enemy_id: str
    model_config = ConfigDict(from_attributes=True)


class LocationUpdateResult(BaseModel):
    session_id: str
    location: str
    model_config = ConfigDict(from_attributes=True)


class RemoveEntityResult(BaseModel):
    status: str
    model_config = ConfigDict(from_attributes=True)


class PhaseChangeResult(BaseModel):
    session_id: str
    current_phase: str
    model_config = ConfigDict(from_attributes=True)


class TurnAddResult(BaseModel):
    session_id: str
    current_turn: int
    model_config = ConfigDict(from_attributes=True)


class ActChangeResult(BaseModel):
    session_id: str
    current_phase: str = ""  # Default to empty if not provided
    current_act: int
    model_config = ConfigDict(from_attributes=True)


class SequenceChangeResult(BaseModel):
    session_id: str
    current_sequence: int
    model_config = ConfigDict(from_attributes=True)


class SpawnResult(BaseModel):
    # Common fields for spawned entities
    id: str  # instance id
    name: str
    model_config = ConfigDict(from_attributes=True)


class FunctionResult(BaseModel):
    # Generic result for function calls
    result: Any
    model_config = ConfigDict(from_attributes=True)


# ====================================================================
# 설정 및 초기화
# ====================================================================

# Query 폴더 경로 (현재 파일이 state_db/Query/query.py에 위치)
QUERY_DIR = Path(__file__).parent

# SQL 쿼리 캐시
SQL_CACHE: Dict[str, str] = {}


def load_all_queries() -> None:
    """QUERY_DIR 내의 모든 .sql 파일을 읽어 캐시에 저장"""
    global SQL_CACHE
    print("📂 Loading SQL files into cache...")
    count = 0
    for sql_file in QUERY_DIR.rglob("*.sql"):
        try:
            with open(sql_file, "r", encoding="utf-8") as f:
                # 절대 경로를 키로 사용
                SQL_CACHE[str(sql_file.resolve())] = f.read()
                count += 1
        except Exception as e:
            print(f"⚠️ Failed to load {sql_file}: {e}")
    print(f"✅ Loaded {count} SQL files into cache")


# ====================================================================
# Connection Pool 관리 클래스
# ====================================================================


class DatabaseManager:
    """
    DB 연결 풀을 관리하는 싱글톤 클래스
    - 매번 연결/종료하지 않고 풀에서 재사용
    - 비동기 컨텍스트 매니저로 안전한 연결 관리
    """

    _pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        """Connection Pool 생성 또는 기존 풀 반환"""
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(
                **DB_CONFIG,
                min_size=2,  # 최소 연결 수
                max_size=10,  # 최대 연결 수
                command_timeout=60,  # 쿼리 타임아웃 (초)
            )
        return cls._pool

    @classmethod
    async def close_pool(cls) -> None:
        """애플리케이션 종료 시 풀 정리"""
        if cls._pool:
            await cls._pool.close()
            cls._pool = None

    @classmethod
    @asynccontextmanager
    async def get_connection(cls) -> Any:
        """
        안전한 연결 획득/반환을 위한 컨텍스트 매니저
        사용 예: async with DatabaseManager.get_connection() as conn:
        """
        pool = await cls.get_pool()
        async with pool.acquire() as connection:
            yield connection


# ====================================================================
# Apache AGE 세션 설정
# ====================================================================


async def set_age_path(conn: asyncpg.Connection) -> None:
    """
    Apache AGE 사용을 위한 세션 설정
    AGE 관련 함수에서만 호출해야 함 (일반 SQL에서는 호출 X)
    """
    await conn.execute('SET search_path = ag_catalog, "$user", public;')


# ====================================================================
# Apache AGE 그래프 초기화
# ====================================================================


async def init_age_graph() -> None:
    """
    Apache AGE 확장 로드 및 그래프 생성
    - AGE는 이미 superuser가 설치했다고 가정
    """
    async with DatabaseManager.get_connection() as conn:
        # search_path 설정 (AGE 작업용)
        await set_age_path(conn)

        # 그래프 존재 여부 확인
        graph_exists = await conn.fetchval(
            "SELECT EXISTS (SELECT 1 FROM ag_catalog.ag_graph WHERE name = $1)",
            AGE_GRAPH_NAME,
        )

        if not graph_exists:
            await conn.execute(
                "SELECT create_graph($1);",
                AGE_GRAPH_NAME,
            )
            print(f"✅ Graph '{AGE_GRAPH_NAME}' created")
        else:
            print(f"✅ Graph '{AGE_GRAPH_NAME}' already exists")


# ====================================================================
# SQL/Cypher 실행 유틸리티 함수
# ====================================================================


async def run_sql_query(
    sql_path: str | Path, params: Optional[List[Any]] = None
) -> List[Dict[str, Any]]:
    """
    SELECT 쿼리 실행 (결과 반환)

    Args:
        sql_path: SQL 파일 경로
        params: 쿼리 파라미터 리스트 (예: [player_id, session_id])

    Returns:
        쿼리 결과 리스트 (각 행은 dict)
    """
    sql_path = Path(sql_path).resolve()
    sql_key = str(sql_path)

    # 캐시 확인
    if sql_key in SQL_CACHE:
        query = SQL_CACHE[sql_key]
    else:
        # 캐시에 없으면 파일 읽기 (개발 중 핫 리로드 지원 등을 위해)
        if not sql_path.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_path}")

        with open(sql_path, "r", encoding="utf-8") as f:
            query = f.read()
            # 런타임에 읽은 것도 캐시에 추가?
            # 일단은 추가하여 다음 호출 시 빠르게 함
            SQL_CACHE[sql_key] = query

    # 연결 풀에서 연결 획득 후 쿼리 실행
    async with DatabaseManager.get_connection() as conn:
        await set_age_path(conn)  # AGE 사용을 위한 설정
        if params:
            rows = await conn.fetch(query, *params)
        else:
            rows = await conn.fetch(query)

    # asyncpg Record를 dict로 변환
    return [dict(row) for row in rows]


async def run_sql_command(
    sql_path: str | Path, params: Optional[List[Any]] = None
) -> str:
    """
    INSERT/UPDATE/DELETE 쿼리 실행 (결과 없음)

    Args:
        sql_path: SQL 파일 경로
        params: 쿼리 파라미터 리스트

    Returns:
        실행 결과 상태 문자열 (예: "INSERT 0 3")
    """
    sql_path = Path(sql_path).resolve()
    sql_key = str(sql_path)

    if sql_key in SQL_CACHE:
        query = SQL_CACHE[sql_key]
    else:
        if not sql_path.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_path}")

        with open(sql_path, "r", encoding="utf-8") as f:
            query = f.read()
            SQL_CACHE[sql_key] = query

    async with DatabaseManager.get_connection() as conn:
        await set_age_path(conn)  # AGE 사용을 위한 설정
        if params:
            result = await conn.execute(query, *params)
        else:
            result = await conn.execute(query)

    return str(result)  # "INSERT 0 5" 같은 문자열 반환


async def run_cypher_query(
    cypher: str, params: Optional[List[Any]] = None
) -> List[Dict[str, Any]]:
    async with DatabaseManager.get_connection() as conn:
        await set_age_path(conn)

        wrapped_query = f"""
            SELECT result::jsonb
            FROM cypher('{AGE_GRAPH_NAME}', $$
                {cypher}
            $$) AS (result agtype);
        """

        if params:
            rows = await conn.fetch(wrapped_query, *params)
        else:
            rows = await conn.fetch(wrapped_query)

    return [row["result"] for row in rows]


async def execute_sql_function(
    function_name: str, params: Optional[List[Any]] = None
) -> List[Dict[str, Any]]:
    """
    PostgreSQL 함수 직접 호출 (create_session 등)

    Args:
        function_name: 함수 이름 (예: 'create_session')
        params: 함수 파라미터 리스트

    Returns:
        함수 실행 결과
    """
    async with DatabaseManager.get_connection() as conn:
        await set_age_path(conn)

        if params:
            placeholders = ", ".join([f"${i + 1}" for i in range(len(params))])
            query = f"SELECT {function_name}({placeholders})"
            rows = await conn.fetch(query, *params)
        else:
            query = f"SELECT {function_name}()"
            rows = await conn.fetch(query)

    return [dict(row) for row in rows]


# ====================================================================
# 메인 테이블 생성
# ====================================================================


async def create_main_tables() -> None:
    """FIRST 디렉토리의 모든 DDL 실행하여 메인 테이블 생성"""
    ddl_files = [
        "scenario.sql",
        "session.sql",
        "player.sql",
        "npc.sql",
        "enemy.sql",
        "item.sql",
        "inventory.sql",
        "player_inventory.sql",
        "player_npc_relations.sql",
        "phase_history.sql",
        "turn_history.sql",
    ]

    async with DatabaseManager.get_connection() as conn:
        for ddl_file in ddl_files:
            print(f"📝 Starting {ddl_file}...")
            ddl_path = QUERY_DIR / "FIRST" / ddl_file

            if not ddl_path.exists():
                print(f"⚠️  {ddl_file} not found, skipping...")
                continue

            with open(ddl_path, "r", encoding="utf-8") as f:
                ddl_sql = f.read()

            try:
                await conn.execute(ddl_sql)
                print(f"✅ {ddl_file} executed")
            except Exception as e:
                print(f"❌ {ddl_file} failed: {e}")
                raise

    print("✅ All main tables created")


# ====================================================================
# 세션 관리 함수들
# ====================================================================


async def session_start(
    scenario_id: str,
    current_act: int = 1,
    current_sequence: int = 1,
    location: str = "Starting Town",
) -> SessionInfo:
    """
    게임 세션 시작
    - create_session 함수 호출하여 세션 생성
    - 트리거로 player 자동 생성

    Args:
        scenario_id: 시나리오 UUID
        current_act: 시작 Act (기본값: 1)
        current_sequence: 시작 Sequence (기본값: 1)
        location: 시작 위치 (기본값: "Starting Town")

    Returns:
        SessionInfo
    """
    # scenario_id를 UUID 객체로 변환 (PostgreSQL UUID 타입 매칭을 위해)
    try:
        scenario_uuid = UUID(scenario_id)
    except (ValueError, AttributeError) as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid scenario_id format: {scenario_id}"
        ) from e

    # create_session 함수 호출
    result = await execute_sql_function(
        "create_session", [scenario_uuid, current_act, current_sequence, location]
    )

    session_id = result[0].get("create_session") if result else None

    if not session_id:
        raise Exception("Failed to create session")

    # 생성된 세션 정보 조회
    sql_path = QUERY_DIR / "INQUIRY" / "Session_show.sql"
    session_info_list = await run_sql_query(sql_path, [session_id])

    if not session_info_list:
        raise Exception("Failed to retrieve session info")

    return SessionInfo.model_validate(session_info_list[0])


async def session_end(session_id: str) -> Dict[str, str]:
    """
    게임 세션 종료

    Args:
        session_id: 종료할 세션 UUID

    Returns:
        {"status": "success", "message": "Session ended"}
    """
    sql_path = QUERY_DIR / "MANAGE" / "session" / "end_session.sql"
    await run_sql_command(sql_path, [session_id])

    return {"status": "success", "message": f"Session {session_id} ended"}


async def session_pause(session_id: str) -> Dict[str, str]:
    """
    게임 세션 일시정지

    Args:
        session_id: 일시정지할 세션 UUID

    Returns:
        {"status": "success", "message": "Session paused"}
    """
    sql_path = QUERY_DIR / "MANAGE" / "session" / "pause_session.sql"
    await run_sql_command(sql_path, [session_id])

    return {"status": "success", "message": f"Session {session_id} paused"}


async def session_resume(session_id: str) -> Dict[str, str]:
    """
    게임 세션 재개

    Args:
        session_id: 재개할 세션 UUID

    Returns:
        {"status": "success", "message": "Session resumed"}
    """
    sql_path = QUERY_DIR / "MANAGE" / "session" / "resume_session.sql"
    await run_sql_command(sql_path, [session_id])

    return {"status": "success", "message": f"Session {session_id} resumed"}


# ====================================================================
# 세션 조회
# ====================================================================


async def get_active_sessions() -> List[SessionInfo]:
    """
    활성 세션 목록 조회

    Returns:
        활성 세션 정보 리스트
    """
    sql_path = QUERY_DIR / "INQUIRY" / "Session_active.sql"
    results = await run_sql_query(sql_path)
    return [SessionInfo.model_validate(row) for row in results]


async def get_session_info(session_id: str) -> SessionInfo:
    """
    세션 상세 정보 조회

    Args:
        session_id: 세션 UUID

    Returns:
        세션 정보
    """
    sql_path = QUERY_DIR / "INQUIRY" / "Session_show.sql"
    result = await run_sql_query(sql_path, [session_id])
    if result:
        return SessionInfo.model_validate(result[0])
    raise HTTPException(status_code=404, detail="Session not found")


# ====================================================================
# 인벤토리 조회
# ====================================================================


async def get_session_inventory(session_id: str) -> List[InventoryItem]:
    """
    세션의 플레이어 인벤토리 조회

    Args:
        session_id: 세션 UUID

    Returns:
        InventoryItem list
    """
    sql_path = QUERY_DIR / "INQUIRY" / "Session_inventory.sql"
    results = await run_sql_query(sql_path, [session_id])
    return [InventoryItem.model_validate(row) for row in results]


# ====================================================================
# NPC 조회
# ====================================================================


async def get_session_npcs(session_id: str) -> List[NPCInfo]:
    """
    세션의 NPC 목록 조회

    Args:
        session_id: 세션 UUID

    Returns:
        NPC 정보 리스트
    """
    sql_path = QUERY_DIR / "INQUIRY" / "Session_npc.sql"
    results = await run_sql_query(sql_path, [session_id])
    return [NPCInfo.model_validate(row) for row in results]


async def get_npc_relations(player_id: str) -> List[NPCRelation]:
    """
    특정 플레이어의 NPC 호감도 조회

    Args:
        player_id: 플레이어 UUID

    Returns:
        NPC relation list
    """
    sql_path = QUERY_DIR / "INQUIRY" / "Npc_relations.sql"
    results = await run_sql_query(sql_path, [player_id])
    return [NPCRelation.model_validate(row) for row in results]


# ====================================================================
# Enemy 조회
# ====================================================================


async def get_session_enemies(
    session_id: str, active_only: bool = True
) -> List[EnemyInfo]:
    """
    세션의 Enemy 목록 조회

    Args:
        session_id: 세션 UUID
        active_only: True면 생존한 적만, False면 전체

    Returns:
        Enemy 정보 리스트
    """
    sql_path = QUERY_DIR / "INQUIRY" / "Session_enemy.sql"
    results = await run_sql_query(sql_path, [session_id, active_only])
    return [EnemyInfo.model_validate(row) for row in results]


# ====================================================================
# 플레이어 상태 조회
# ====================================================================


async def get_player_stats(player_id: str) -> PlayerStats:
    """
    플레이어 상세 스탯 조회

    Args:
        player_id: 플레이어 UUID

    Returns:
        PlayerStats
    """
    sql_path = QUERY_DIR / "INQUIRY" / "Player_stats.sql"
    result = await run_sql_query(sql_path, [player_id])
    if result:
        return PlayerStats.model_validate(result[0])
    raise HTTPException(status_code=404, detail="Player not found")


async def get_player_state(player_id: str) -> FullPlayerState:
    """
    플레이어 전체 상태 조회 (요구사항 스펙)

    Args:
        player_id: 조회할 플레이어 UUID

    Returns:
        FullPlayerState
    """
    try:
        # 플레이어 기본 정보 조회
        player_data = await get_player_stats(player_id)
    except Exception:
        # 플레이어가 존재하지 않으면 빈 결과 반환
        return FullPlayerState(
            player=PlayerStateResponse(hp=0, gold=0, items=[]),
            player_npc_relations=[],
        )

    # NPC 관계 조회
    npc_relations = await get_npc_relations(player_id)

    # state Pydantic 모델에서 값 추출
    state = player_data.state
    numeric_state = state.numeric

    # 인벤토리에서 아이템 ID 목록 추출 (별도 쿼리 필요)
    # TODO: player_inventory 테이블에서 조회하도록 수정 필요
    items: List[int] = []  # 임시: 빈 리스트

    return FullPlayerState(
        player=PlayerStateResponse(
            hp=numeric_state.HP or 0,
            gold=numeric_state.gold or 0,
            items=items,
        ),
        player_npc_relations=npc_relations,
    )


# ====================================================================
# 아이템 조회 (아직 구현 안됨 - 향후 추가)
# ====================================================================


async def get_item_info(item_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    아이템 정보 조회

    Args:
        item_id: 특정 아이템 ID (None이면 전체 조회)

    Returns:
        아이템 정보 리스트
    """
    # TODO: Query/INQUIRY/Item_info.sql 파일 생성 필요
    # 임시로 빈 리스트 반환
    return []


async def inventory_update(
    player_id: str, item_id: int, quantity: int
) -> Dict[str, Any]:
    """
    플레이어 인벤토리 업데이트

    Args:
        player_id: 플레이어 UUID
        item_id: 아이템 ID
        quantity: 수량 변화 (양수: 추가, 음수: 제거)

    Returns:
        업데이트된 인벤토리 정보
    """
    # TODO: Query/UPDATE/update_inventory.sql 파일 생성 필요
    # 임시로 빈 결과 반환
    return {"player_id": player_id, "inventory": []}


# ====================================================================
# 플레이어 상태 업데이트
# ====================================================================


async def update_player_hp(
    player_id: str, session_id: str, hp_change: int, reason: str = "unknown"
) -> PlayerHPUpdateResult:
    """
    플레이어 HP 변경

    Args:
        player_id: 플레이어 UUID
        session_id: 세션 UUID
        hp_change: HP 변화량 (양수: 회복, 음수: 피해)
        reason: 변경 사유 (combat, item, rest 등)

    Returns:
        PlayerHPUpdateResult
    """
    sql_path = QUERY_DIR / "UPDATE" / "update_player_hp.sql"
    result = await run_sql_query(sql_path, [player_id, session_id, hp_change])

    if result:
        return PlayerHPUpdateResult.model_validate(result[0])
    raise HTTPException(status_code=404, detail="Player or Session not found")


async def update_player_stats(
    player_id: str, session_id: str, stat_changes: Dict[str, int]
) -> PlayerStats:
    """
    플레이어 스탯 변경 (범용)

    Args:
        player_id: 플레이어 UUID
        session_id: 세션 UUID
        stat_changes: 변경할 스탯들 {"HP": -10, "MP": 5, "STR": 1}

    Returns:
        업데이트된 플레이어 상태
    """
    sql_path = QUERY_DIR / "UPDATE" / "update_player_stats.sql"
    # stat_changes를 JSONB로 변환하여 전달
    await run_sql_command(sql_path, [player_id, session_id, stat_changes])

    return await get_player_stats(player_id)


# ====================================================================
# NPC 상태 업데이트
# ====================================================================


async def update_npc_affinity(
    player_id: str, npc_id: str, affinity_change: int
) -> NPCAffinityUpdateResult:
    """
    NPC 호감도 변경

    Args:
        player_id: 플레이어 UUID
        npc_id: NPC UUID
        affinity_change: 호감도 변화량 (양수/음수)

    Returns:
        NPCAffinityUpdateResult
    """
    sql_path = QUERY_DIR / "UPDATE" / "update_npc_affinity.sql"
    result = await run_sql_query(sql_path, [player_id, npc_id, affinity_change])

    if result:
        return NPCAffinityUpdateResult(
            player_id=player_id,
            npc_id=npc_id,
            new_affinity=result[0].get("new_affinity", 0),
        )
    else:
        return NPCAffinityUpdateResult(
            player_id=player_id, npc_id=npc_id, new_affinity=0
        )


# ====================================================================
# Enemy 상태 업데이트
# ====================================================================


async def update_enemy_hp(
    enemy_instance_id: str, session_id: str, hp_change: int
) -> EnemyHPUpdateResult:
    """
    적 HP 변경

    Args:
        enemy_instance_id: 적 인스턴스 UUID
        session_id: 세션 UUID
        hp_change: HP 변화량 (보통 음수)

    Returns:
        EnemyHPUpdateResult
    """
    sql_path = QUERY_DIR / "UPDATE" / "update_enemy_hp.sql"
    result = await run_sql_query(sql_path, [enemy_instance_id, session_id, hp_change])

    if result:
        return EnemyHPUpdateResult.model_validate(result[0])
    raise HTTPException(status_code=404, detail="Enemy or Session not found")


async def defeat_enemy(enemy_instance_id: str, session_id: str) -> DefeatEnemyResult:
    """
    적 처치 처리

    Args:
        enemy_instance_id: 적 인스턴스 UUID
        session_id: 세션 UUID

    Returns:
        DefeatEnemyResult
    """
    sql_path = QUERY_DIR / "UPDATE" / "defeated_enemy.sql"
    await run_sql_command(sql_path, [enemy_instance_id, session_id])

    return DefeatEnemyResult(status="defeated", enemy_id=enemy_instance_id)


# ====================================================================
# 위치 업데이트
# ====================================================================


async def update_location(session_id: str, new_location: str) -> LocationUpdateResult:
    """
    세션 위치 변경

    Args:
        session_id: 세션 UUID
        new_location: 새 위치 이름

    Returns:
        LocationUpdateResult
    """
    sql_path = QUERY_DIR / "UPDATE" / "update_location.sql"
    await run_sql_command(sql_path, [session_id, new_location])

    return LocationUpdateResult(session_id=session_id, location=new_location)


# ====================================================================
# Enemy 관리
# ====================================================================


async def spawn_enemy(session_id: str, enemy_data: Dict[str, Any]) -> SpawnResult:
    """
    적 동적 생성

    Args:
        session_id: 세션 UUID
        enemy_data: {
            "enemy_id": 1,
            "name": "Goblin Warrior",
            "hp": 30,
            "attack": 10,
            "defense": 5
        }

    Returns:
        생성된 적 정보 (enemy_instance_id 포함)
    """
    sql_path = QUERY_DIR / "MANAGE" / "enemy" / "spawn_enemy.sql"
    params = [
        session_id,
        enemy_data.get("enemy_id"),
        enemy_data.get("name"),
        enemy_data.get("description", ""),
        enemy_data.get("hp", 30),
        enemy_data.get("attack", 10),
        enemy_data.get("defense", 5),
        enemy_data.get("tags", ["enemy"]),
    ]
    result = await run_sql_query(sql_path, params)

    if result:
        # DB returns enemy_instance_id, mapping it to SpawnResult.id
        row = result[0]
        return SpawnResult(
            id=row.get("enemy_instance_id", ""), name=row.get("name", "")
        )
    raise HTTPException(status_code=500, detail="Failed to spawn enemy")


async def remove_enemy(enemy_instance_id: str, session_id: str) -> RemoveEntityResult:
    """
    적 제거 (물리적 삭제)

    Args:
        enemy_instance_id: 적 인스턴스 UUID
        session_id: 세션 UUID

    Returns:
        RemoveEntityResult
    """
    sql_path = QUERY_DIR / "MANAGE" / "enemy" / "remove_enemy.sql"
    await run_sql_command(sql_path, [enemy_instance_id, session_id])

    return RemoveEntityResult(status="removed")


# ====================================================================
# NPC 관리
# ====================================================================


async def spawn_npc(session_id: str, npc_data: Dict[str, Any]) -> SpawnResult:
    """
    NPC 동적 생성

    Args:
        session_id: 세션 UUID
        npc_data: {
            "npc_id": 1,
            "name": "Merchant Tom",
            "description": "A friendly merchant"
        }

    Returns:
        생성된 NPC 정보
    """
    sql_path = QUERY_DIR / "MANAGE" / "npc" / "spawn_npc.sql"
    params = [
        session_id,
        npc_data.get("npc_id"),
        npc_data.get("name"),
        npc_data.get("description", ""),
        npc_data.get("hp", 100),
        npc_data.get("tags", ["npc"]),
    ]
    result = await run_sql_query(sql_path, params)

    if result:
        row = result[0]
        return SpawnResult(id=row.get("npc_instance_id", ""), name=row.get("name", ""))
    raise HTTPException(status_code=500, detail="Failed to spawn NPC")


async def remove_npc(npc_instance_id: str, session_id: str) -> RemoveEntityResult:
    """
    NPC 제거

    Args:
        npc_instance_id: NPC 인스턴스 UUID
        session_id: 세션 UUID

    Returns:
        RemoveEntityResult
    """
    sql_path = QUERY_DIR / "MANAGE" / "npc" / "remove_npc.sql"
    await run_sql_command(sql_path, [npc_instance_id, session_id])

    return RemoveEntityResult(status="removed")


# ====================================================================
# Phase 관리
# ====================================================================


async def change_phase(session_id: str, new_phase: str) -> PhaseChangeResult:
    """
    Phase 전환

    Args:
        session_id: 세션 UUID
        new_phase: 새 Phase (exploration, combat, dialogue, rest)

    Returns:
        PhaseChangeResult
    """
    sql_path = QUERY_DIR / "MANAGE" / "phase" / "change_phase.sql"
    await run_sql_command(sql_path, [session_id, new_phase])

    return PhaseChangeResult(session_id=session_id, current_phase=new_phase)


async def get_current_phase(session_id: str) -> PhaseChangeResult:
    """
    현재 Phase 조회

    Args:
        session_id: 세션 UUID

    Returns:
        Phase 정보
    """
    sql_path = QUERY_DIR / "INQUIRY" / "Session_phase.sql"
    result = await run_sql_query(sql_path, [session_id])

    if result:
        return PhaseChangeResult.model_validate(result[0])
    raise HTTPException(status_code=404, detail="Session phase not found")


# ====================================================================
# Turn 관리
# ====================================================================


async def add_turn(session_id: str) -> TurnAddResult:
    """
    Turn 증가

    Args:
        session_id: 세션 UUID

    Returns:
        TurnAddResult
    """
    sql_path = QUERY_DIR / "MANAGE" / "turn" / "add_turn.sql"
    result = await run_sql_query(sql_path, [session_id])

    # Check if result is empty or handle casting correctly
    if result:
        return TurnAddResult.model_validate(result[0])
    raise HTTPException(status_code=404, detail="Session not found")


async def get_current_turn(session_id: str) -> TurnAddResult:
    """
    현재 Turn 조회

    Args:
        session_id: 세션 UUID

    Returns:
        Turn 정보
    """
    sql_path = QUERY_DIR / "INQUIRY" / "Session_turn.sql"
    result = await run_sql_query(sql_path, [session_id])

    if result:
        return TurnAddResult.model_validate(result[0])
    raise HTTPException(status_code=404, detail="Session turn not found")


# ====================================================================
# Act/Sequence 관리
# ====================================================================


async def change_act(session_id: str, new_act: int) -> ActChangeResult:
    """
    Act 변경

    Args:
        session_id: 세션 UUID
        new_act: 새 Act 번호

    Returns:
        ActChangeResult
    """
    sql_path = QUERY_DIR / "MANAGE" / "act" / "select_act.sql"
    await run_sql_command(sql_path, [session_id, new_act])

    return ActChangeResult(session_id=session_id, current_act=new_act)


async def change_sequence(session_id: str, new_sequence: int) -> SequenceChangeResult:
    """
    Sequence 변경

    Args:
        session_id: 세션 UUID
        new_sequence: 새 Sequence 번호

    Returns:
        SequenceChangeResult
    """
    sql_path = QUERY_DIR / "MANAGE" / "sequence" / "select_sequence.sql"
    await run_sql_command(sql_path, [session_id, new_sequence])

    return SequenceChangeResult(session_id=session_id, current_sequence=new_sequence)


# ====================================================================
# 그래프 조회 (서브그래프 시각화용)
# ====================================================================


async def get_graph_nodes(label: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    그래프의 노드 조회

    Args:
        label: 노드 라벨 (예: 'player', 'item'). None이면 전체 조회

    Returns:
        노드 정보 리스트
    """
    if label:
        cypher = f"MATCH (n:{label}) RETURN n"
    else:
        cypher = "MATCH (n) RETURN n"

    return await run_cypher_query(cypher)


async def get_graph_edges(edge_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    그래프의 엣지 조회

    Args:
        edge_type: 엣지 타입 (예: 'EARN_ITEM', 'PLAYER_INVENTORY'). None이면 전체 조회

    Returns:
        엣지 정보 리스트
    """
    if edge_type:
        cypher = f"MATCH ()-[r:{edge_type}]->() RETURN r"
    else:
        cypher = "MATCH ()-[r]->() RETURN r"

    return await run_cypher_query(cypher)


async def get_subgraph(
    center_id: str, depth: int = 1
) -> Dict[str, List[Dict[str, Any]]]:
    """
    특정 노드를 중심으로 서브그래프 조회

    Args:
        center_id: 중심 노드 ID
        depth: 탐색 깊이

    Returns:
        {"paths": [...]}
    """
    # 노드와 연결된 엣지 조회
    cypher = f"""
        MATCH path = (center {{id: '{center_id}'}})-[*1..{depth}]-(connected)
        RETURN path
    """
    paths = await run_cypher_query(cypher)

    return {"paths": paths}


# ====================================================================
# 앱 생명주기 관리용
# ====================================================================


async def startup() -> None:
    """FastAPI 시작 시 호출 - Connection Pool 및 AGE 그래프 초기화"""
    await DatabaseManager.get_pool()
    print("✅ Database connection pool initialized")

    # SQL 쿼리 로드
    load_all_queries()

    # 메인 테이블 및 함수 생성
    try:
        await create_main_tables()
        print("✅ Main tables and functions ready")
    except Exception as e:
        print(f"⚠️  Table initialization warning: {e}")

    # Apache AGE 그래프 초기화
    await init_age_graph()
    print(f"✅ Apache AGE graph '{AGE_GRAPH_NAME}' ready")


async def shutdown() -> None:
    """FastAPI 종료 시 호출 - Connection Pool 정리"""
    await DatabaseManager.close_pool()
    print("🔒 Database connection pool closed")
