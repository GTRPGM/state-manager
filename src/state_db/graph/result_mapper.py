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

        # 투명한 매핑 보강: 래퍼를 벗기고 순수 데이터 반환 시도
        if isinstance(parsed, dict) and "__age_type__" in parsed:
            age_type = parsed["__age_type__"]
            if age_type == "map":
                return parsed["value"]
            if age_type == "scalar":
                return parsed["value"]
            # vertex/edge는 properties가 중요하지만 모델 구성을 위해 그대로 유지하거나
            # 선택적 반환. 여기서는 호환성을 위해 properties가 있으면
            # 우선적으로 활용하도록 유도
        return parsed

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

        # 만약 ::type 접미사가 없다면, JSON 형태인지 확인 후 파싱 시도
        m = ResultMapper.TYPE_ANNOTATION_PATTERN.search(val)
        if not m:
            # 1. JSON Map/List 형태인지 확인
            stripped = val.strip()
            if (stripped.startswith("{") and stripped.endswith("}")) or (
                stripped.startswith("[") and stripped.endswith("]")
            ):
                try:
                    data = json.loads(val)
                    if isinstance(data, dict):
                        return {
                            "__age_type__": "map",
                            "value": data,
                        }
                    if isinstance(data, list):
                        return {
                            "__age_type__": "list",
                            "value": data,
                        }
                except Exception:
                    pass

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

        if age_type in ("map", "object"):
            return ResultMapper._parse_map(raw)

        # fallback
        return ResultMapper._safe_json(age_type, raw)

    @staticmethod
    def _parse_map(raw: str) -> Any:
        data = ResultMapper._safe_json(None, raw)
        if isinstance(data, dict):
            # 내부 값들도 재귀적으로 파싱할 수 있으나,
            # 일단 Map 자체를 반환 (이미 json.loads된 상태)
            return {
                "__age_type__": "map",
                "value": data,
            }
        return data

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
