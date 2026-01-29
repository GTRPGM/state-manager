# Refactoring Plan

## 목적

500줄 이상의 대형 파일들을 기능별로 분할하여 유지보수수를 높이고 가독성을 개선함.

## 대상 파일

1. `src/state_db/schemas.py` (788 lines)
2. `src/state_db/data/node/core/session_Query.sql` (766 lines)
3. `src/state_db/Query/TRACE/phase_tracing-r.sql` (701 lines)
4. `src/state_db/data/node/core/m_act_seq.sql` (692 lines)
5. `src/state_db/Query/DEBUG/concept-r.sql` (647 lines)

## 진행 현황

- [x] `src/state_db/schemas.py` 분할
- [x] `src/state_db/data/node/core/session_Query.sql` 분할 및 삭제 (중복 제거)
- [x] `src/state_db/Query/TRACE/phase_tracing-r.sql` 분할
- [x] `src/state_db/data/node/core/m_act_seq.sql` 분할 및 삭제 (중복 제거)
- [x] `src/state_db/Query/DEBUG/concept-r.sql` 분할 및 삭제 (중복 제거)

## 2차 리팩터링 (Python 파일 200줄 이하 목표)

- [ ] `src/state_db/infrastructure/database.py`: 스키마 초기화 로직 분리
- [ ] `src/state_db/repositories/session.py`: 월드 상태 관리 로직 분리
- [ ] `src/state_db/routers/router_TRACE.py`: Turn/Phase 라우터 분리
- [ ] `src/state_db/models/__init__.py`: 모델 정의 파일 분산

## 상세 계획

### 1. `src/state_db/schemas.py` 분할

- `src/state_db/schemas/` 디렉토리 생성
- `base.py`: 공통 Enum 및 Base 클래스
- `session.py`: 세션 관련 스키마
- `inventory.py`: 인벤토리 관련 스키마
- `item.py`: 아이템 관련 스키마
- `player.py`: 플레이어 관련 스키마
- `npc.py`: NPC 관련 스키마
- `enemy.py`: 적(Enemy) 관련 스키마
- `world.py`: 위치, Phase, Act, Sequence 관련 스키마
- `scenario.py`: 시나리오 주입 관련 스키마
- `__init__.py`: 모든 스키마 export 및 기존 경로 호환성 유지

### 2. SQL 파일 분할

- SQL 파일들도 기능별로 쪼개어 가독성 확보
- Apache AGE 쿼리 특성상 연관된 로직끼리 묶어서 분리

#### 2.1 `src/state_db/Query/TRACE/phase_tracing-r.sql` 분할

- `src/state_db/Query/TRACE/phase/` 디렉토리 하위로 이동
- `get_history.sql`: 전체 Phase 전환 이력
- `get_recent.sql`: 최근 Phase 전환
- `get_by_phase.sql`: 특정 Phase 필터링
- `get_range.sql`: Turn 범위 필터링
- `get_latest.sql`: 최신 Phase 전환
- `get_statistics.sql`: Phase 통계
- `get_pattern.sql`: Phase 패턴
- `get_summary.sql`: Phase 요약

#### 2.2 `src/state_db/data/node/core/session_Query.sql` 분할

- `src/state_db/Query/INQUIRY/session/` 및 `src/state_db/Query/MANAGE/session/` 등으로 분산 배치
- 중복되거나 통합된 쿼리들을 개별 파일로 분리하여 리포지토리에서 관리 용이하게 변경
