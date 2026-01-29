# Current Task: Fix failing test in Trace Router

## 목적

- `tests/test_router_TRACE.py::test_get_latest_turn` 테스트 실패 해결
- FastAPI 라우트 우선순위 문제로 인한 422 에러 수정

## 현황

- `test_get_latest_turn`이 422 Unprocessable Entity 반환
- `/state/session/{session_id}/turn/latest` 요청이 `/state/session/{session_id}/turn/{turn_number}`(int)로 잘못 매칭됨

## 계획

1. `src/state_db/routers/router_TRACE.py`에서 `get_latest_turn_endpoint`를 `get_turn_details_endpoint`보다 먼저 정의하도록 순서 변경
2. `uv run pytest tests/test_router_TRACE.py`로 수정 사항 검증
3. 전체 테스트 재실행하여 영향도 확인

## 진행 상황

- [x] 라우터 순서 변경
- [x] TRACE 라우터 테스트 통과
- [x] 전체 테스트 통과
