import logging
from pathlib import Path
from typing import Dict, Union

logger = logging.getLogger(__name__)


class QueryRegistry:
    """
    Cypher 쿼리 파일을 로딩하고 캐싱하는 레지스트리.
    """

    def __init__(self):
        self._cache: Dict[str, str] = {}

    def get_query(self, query_or_path: str) -> str:
        """
        쿼리 문자열 또는 파일 경로를 받아 실제 Cypher 쿼리를 반환한다.
        """
        if query_or_path.endswith(".cypher"):
            return self.load_from_file(query_or_path)
        return query_or_path

    def load_from_file(self, file_path: Union[str, Path]) -> str:
        path_str = str(Path(file_path).resolve())
        if path_str not in self._cache:
            try:
                with open(path_str, "r", encoding="utf-8") as f:
                    self._cache[path_str] = f.read()
            except Exception as e:
                logger.error(f"Failed to load cypher file {path_str}: {e}")
                raise
        return self._cache[path_str]


# 글로벌 레지스트리 인스턴스
registry = QueryRegistry()
