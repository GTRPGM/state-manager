import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from state_db.configs.setting import AGE_GRAPH_NAME
from state_db.infrastructure.connection import DatabaseManager, set_age_path
from state_db.graph.validator import GraphValidator

logger = logging.getLogger(__name__)

class CypherEngine:
    """
    Apache AGE Cypher 쿼리 실행 엔진.
    파라미터 바인딩, 세션 관리, 결과 매핑을 담당한다.
    """

    def __init__(self, graph_name: str = AGE_GRAPH_NAME):
        self.graph_name = graph_name
        self.query_cache: Dict[str, str] = {}

    def load_query(self, file_path: Union[str, Path]) -> str:
        """파일에서 Cypher 쿼리를 로드하고 캐싱한다."""
        path_str = str(file_path)
        if path_str not in self.query_cache:
            with open(file_path, "r", encoding="utf-8") as f:
                self.query_cache[path_str] = f.read()
        return self.query_cache[path_str]

    async def run_cypher(
        self,
        query_or_path: str,
        params: Optional[Dict[str, Any]] = None,
        validate: bool = False,
        tx: Any = None
    ) -> List[Dict[str, Any]]:
        """
        Cypher 쿼리를 실행한다.
        
        :param query_or_path: .cypher 파일 경로 또는 원본 쿼리 문자열
        :param params: 바인딩할 파라미터 딕셔너리
        :param validate: (Beta) 파라미터 내 엔티티 속성 검증 여부
        :param tx: 외부 트랜잭션 (없으면 새로운 커넥션/트랜잭션 사용)
        :return: 결과 딕셔너리 리스트
        """
        if params is None:
            params = {}

        # 1. 쿼리 준비
        if query_or_path.endswith(".cypher"):
            cypher_sql = self.load_query(query_or_path)
        else:
            cypher_sql = query_or_path

        # 2. 검증 (옵션)
        # 복잡한 로직이므로 현재는 명시적인 props 키가 있을 때만 부분 검증
        if validate and "props" in params:
            # 예: CREATE (:n $props) 패턴 가정
            try:
                # 라벨 추론은 어려우므로 일단 공통 속성만 체크하거나
                # 호출자가 명시적으로 validator를 쓰는 것을 권장
                pass 
            except Exception as e:
                logger.warning(f"Validation warning: {e}")

        # 3. 실행
        # AGE 시그니처 호환성을 위해 첫 번째 인자를 text로 캐스팅하고, 
        # agtype은 ag_catalog.agtype으로 명시적으로 경로를 지정합니다.
        params_json = json.dumps(params)
        
        final_sql = f"""
            SELECT * FROM ag_catalog.cypher(
                $1::text, 
                $2::text, 
                $3::text::ag_catalog.agtype
            ) as (result ag_catalog.agtype);
        """
        
        if tx:
             return await self._execute_with_conn(tx, final_sql, cypher_sql, params_json)
        else:
            async with DatabaseManager.get_connection() as conn:
                await set_age_path(conn)
                return await self._execute_with_conn(conn, final_sql, cypher_sql, params_json)

    async def _execute_with_conn(self, conn, sql, cypher, params_json):
        rows = await conn.fetch(sql, self.graph_name, cypher, params_json)
        
        results = []
        for row in rows:
            # AGE 결과는 agtype(JSON 텍스트)으로 옴.
            # 어떤 쿼리는 스칼라를, 어떤 쿼리는 맵을 반환함.
            val = row[0] # result column
            
            # agtype 디코딩 (여기서는 json.loads와 유사하게 처리)
            # ::vertex, ::edge 등의 애노테이션이 붙어있을 수 있으므로 주의 필요하나
            # asyncpg가 텍스트로 주면 json.loads로 보통 파싱됨.
            if isinstance(val, str):
                try:
                    # 끝에 ::vertex 등이 붙는 경우 처리 (AGE 버전에 따라 다름)
                    # 현재 설정에서는 순수 JSON으로 가정
                    parsed = json.loads(val)
                    results.append(parsed)
                except json.JSONDecodeError:
                    results.append(val)
            else:
                results.append(val)
                
        return results

# 싱글톤 인스턴스 (필요시)
engine = CypherEngine()
