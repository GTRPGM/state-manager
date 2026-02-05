import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from state_db.configs.setting import AGE_GRAPH_NAME
from state_db.graph.query_registry import registry
from state_db.graph.result_mapper import mapper
from state_db.infrastructure.connection import DatabaseManager

logger = logging.getLogger(__name__)


class CypherEngine:
    """
    Apache AGE Cypher 쿼리 실행 엔진 (Phase A 준수).
    쿼리 문자열은 리터럴로 삽입하고, 파라미터는 agtype 바인딩을 사용한다.
    """

    def __init__(self, graph_name: str = AGE_GRAPH_NAME):
        self.graph_name = graph_name

    async def run_cypher(
        self,
        query_or_path: str,
        params: Optional[Dict[str, Any]] = None,
        tx: Any = None,
    ) -> List[Any]:
        """
        Cypher 쿼리를 실행한다.
        """
        if params is None:
            params = {}

        # 1. 쿼리 로드
        cypher_text = registry.get_query(query_or_path)
        params_json = json.dumps(params)

        # 2. SQL 준비
        # AGE의 cypher() 함수는 query_string 인자로 리터럴($$ $$)을
        # 강력하게 권장/요구함.
        # 내부 파라미터($params)는 agtype 인자를 통해 안전하게 전달 가능.
        if params:
            final_sql = f"""
                SELECT * FROM ag_catalog.cypher(
                    '{self.graph_name}',
                    $$ {cypher_text} $$,
                    $1::ag_catalog.agtype
                ) as (result ag_catalog.agtype);
            """
            sql_params = [params_json]
        else:
            final_sql = f"""
                SELECT * FROM ag_catalog.cypher(
                    '{self.graph_name}',
                    $$ {cypher_text} $$
                ) as (result ag_catalog.agtype);
            """
            sql_params = []

        # 3. 실행
        try:
            if tx:
                rows = await tx.fetch(final_sql, *sql_params)
                return mapper.map_results(rows)
            else:
                async with DatabaseManager.get_connection() as conn:
                    rows = await conn.fetch(final_sql, *sql_params)
                    return mapper.map_results(rows)
        except Exception as e:
            logger.error(
                f"Cypher execution failed: {e}\n"
                f"Query: {cypher_text}\nParams: {params_json}"
            )
            raise

    def load_query(self, file_path: Union[str, Path]) -> str:
        return registry.load_from_file(file_path)

    @property
    def query_cache(self):
        return registry._cache


# 싱글톤 인스턴스
engine = CypherEngine()
