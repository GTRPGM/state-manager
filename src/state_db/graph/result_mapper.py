import json
import re
from typing import Any, List


class ResultMapper:
    TYPE_ANNOTATION_PATTERN = re.compile(r"::([a-zA-Z_]+)$")

    @staticmethod
    def map_row(row: Any) -> Any:
        # AGE 쿼리는 단일 컬럼 반환이 정석
        val = row[0] if len(row) > 0 else None
        if val is None:
            return None

        return ResultMapper._parse_agtype(val)

    @staticmethod
    def map_results(rows: List[Any]) -> List[Any]:
        return [ResultMapper.map_row(row) for row in rows]

    @staticmethod
    def _parse_agtype(val: Any) -> Any:
        # asyncpg가 이미 파싱한 타입 (numeric 등)
        if not isinstance(val, str):
            return {
                "__age_type__": "scalar",
                "value": val,
            }

        m = ResultMapper.TYPE_ANNOTATION_PATTERN.search(val)
        if not m:
            return {
                "__age_type__": "scalar",
                "value": val,
            }

        age_type = m.group(1)
        raw = val[: m.start()]

        if age_type in ("vertex", "edge"):
            return ResultMapper._parse_vertex_or_edge(age_type, raw)

        if age_type == "path":
            return ResultMapper._parse_path(raw)

        if age_type in ("list", "array"):
            return ResultMapper._parse_list(raw)

        # fallback
        return ResultMapper._safe_json(age_type, raw)

    @staticmethod
    def _parse_vertex_or_edge(age_type: str, raw: str) -> Any:
        data = ResultMapper._safe_json(None, raw)
        return {
            "__age_type__": age_type,
            "id": data.get("id"),
            "label": data.get("label"),
            "start_id": data.get("start_id"),
            "end_id": data.get("end_id"),
            "properties": data.get("properties", {}),
            "_raw": data,
        }

    @staticmethod
    def _parse_path(raw: str) -> Any:
        data = ResultMapper._safe_json(None, raw)
        # path는 [vertex, edge, vertex, ...] 구조
        elements = []
        for item in data:
            elements.append(ResultMapper._parse_agtype(item))
        return {
            "__age_type__": "path",
            "elements": elements,
        }

    @staticmethod
    def _parse_list(raw: str) -> Any:
        data = ResultMapper._safe_json(None, raw)
        return {
            "__age_type__": "list",
            "value": [ResultMapper._parse_agtype(v) for v in data],
        }

    @staticmethod
    def _safe_json(age_type: str | None, raw: str) -> Any:
        try:
            return json.loads(raw)
        except Exception:
            return {
                "__age_type__": age_type or "unknown",
                "raw": raw,
            }


# 글로벌 매퍼 인스턴스
mapper = ResultMapper()
