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

        parsed = ResultMapper._parse_agtype(val)

        # 투명한 매핑: 래퍼를 벗기고 데이터 반환
        if isinstance(parsed, dict) and "__age_type__" in parsed:
            age_type = parsed["__age_type__"]
            if age_type in ("map", "scalar"):
                return parsed["value"]
        return parsed

    @staticmethod
    def map_results(rows: List[Any]) -> List[Any]:
        return [ResultMapper.map_row(row) for row in rows]

    @staticmethod
    def _parse_agtype(val: Any) -> Any:
        if not isinstance(val, str):
            return {"__age_type__": "scalar", "value": val}

        # 따옴표 제거 (AGE 문자열 리터럴 정규화)
        clean_val = val.strip()
        if clean_val.startswith('"') and clean_val.endswith('"'):
            clean_val = clean_val[1:-1]

        m = ResultMapper.TYPE_ANNOTATION_PATTERN.search(val)
        if not m:
            # JSON 형태 감지 및 파싱
            if (clean_val.startswith("{") and clean_val.endswith("}")) or (
                clean_val.startswith("[") and clean_val.endswith("]")
            ):
                try:
                    data = json.loads(clean_val)
                    return {
                        "__age_type__": "map" if isinstance(data, dict) else "list",
                        "value": data,
                    }
                except Exception:
                    pass
            return {"__age_type__": "scalar", "value": clean_val}

        age_type = m.group(1)
        raw = val[: m.start()]
        if age_type in ("vertex", "edge"):
            return ResultMapper._parse_vertex_or_edge(age_type, raw)
        if age_type == "path":
            return ResultMapper._parse_path(raw)
        if age_type in ("list", "array"):
            return ResultMapper._parse_list(raw)
        if age_type in ("map", "object"):
            return ResultMapper._parse_map(raw)
        return {"__age_type__": "scalar", "value": clean_val}

    @staticmethod
    def _parse_map(raw: str) -> Any:
        data = ResultMapper._safe_json(raw)
        # 내부 값 재귀 파싱 생략 (Repository에서 처리 권장)
        return {"__age_type__": "map", "value": data}

    @staticmethod
    def _parse_vertex_or_edge(age_type: str, raw: str) -> Any:
        data = ResultMapper._safe_json(raw)
        return {
            "__age_type__": age_type,
            "id": data.get("id"),
            "label": data.get("label"),
            "properties": data.get("properties", {}),
            "start_id": data.get("start_id"),
            "end_id": data.get("end_id"),
        }

    @staticmethod
    def _parse_path(raw: str) -> Any:
        data = ResultMapper._safe_json(raw)
        return {
            "__age_type__": "path",
            "elements": [ResultMapper._parse_agtype(item) for item in data],
        }

    @staticmethod
    def _parse_list(raw: str) -> Any:
        data = ResultMapper._safe_json(raw)
        return {"__age_type__": "list", "value": data}

    @staticmethod
    def _safe_json(raw: str) -> Any:
        try:
            return json.loads(raw)
        except Exception:
            return {}


mapper = ResultMapper()
