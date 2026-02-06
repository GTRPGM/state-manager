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

        # 1. 쿼리 로드 및 정규화
        raw_cypher = registry.get_query(query_or_path)

        # 주석 제거 및 한 줄 변환
        # 1. 줄 단위로 분리
        lines = raw_cypher.splitlines()
        # 2. 각 줄에서 // 주석 제거 (단순화된 처리: //가 있으면 그 뒤는 무시)
        cleaned_lines = []
        for line in lines:
            if "//" in line:
                line = line.split("//")[0]
            cleaned_lines.append(line.strip())

        # 3. 공백으로 연결하여 한 줄로 만듦
        cypher_text = " ".join(filter(None, cleaned_lines))

        params_json = json.dumps(params)

        # 2. SQL 준비
        # AGE의 cypher() 함수는 첫 번째 인자로 리터럴($$ $$)을 강력히 요구함.
        # 파라미터($1)로 전달 시 'a dollar-quoted string constant is expected'
        # 에러 발생.
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
