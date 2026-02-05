# Architecture v0.0.0

## Summary
- FastAPI 기반의 상태 관리 서버로, RDBMS(SQL)와 GraphDB(Cypher)를 결합한 하이브리드 아키텍처를 채택하고 있습니다.

## Context
- GTRPGM 시스템 내에서 게임의 정적 데이터(시나리오, 아이템 등)와 동적 데이터(세션 상태, 플레이어 위치 등)를 영속적으로 관리하기 위해 구축되었습니다.

## System overview
- **Web Framework**: FastAPI
- **Database**: PostgreSQL + Apache AGE (Apache Graph Extension)
- **Data Access**: SQL 및 Cypher 쿼리를 파일(`src/state_db/Query`)로 분리하여 로드 및 실행
- **Main Modules**:
    - `infrastructure`: DB 연결 및 생명주기 관리
    - `graph`: Cypher 엔진 및 결과 매핑
    - `repositories`: 도메인별 데이터 접근 로직
    - `routers`: API 엔드포인트 정의 (INQUIRY, UPDATE, MANAGE 등)

## Data flow
1. 클라이언트 API 요청 (FastAPI Router)
2. 서비스 레이어 또는 리포지토리 레이어에서 데이터 처리 요청
3. `query_executor`를 통해 SQL/Cypher 쿼리 로드 및 실행
4. Apache AGE를 통한 그래프 연산 및 PostgreSQL을 통한 관계형 연산 수행
5. 결과를 Pydantic 모델로 변환하여 클라이언트에 응답

## Decisions
- Decision: SQL/Cypher 파일 분리
- Reason: 쿼리 가독성을 높이고 DB 성능 최적화를 용이하게 하기 위함
- Impact: `src/state_db/Query` 하위의 디렉토리 구조를 엄격히 관리해야 함

- Decision: Apache AGE 사용
- Reason: TRPG의 복잡한 개체 간 관계(플레이어-NPC-아이템-장소)를 유연하게 표현하기 위함
- Impact: AGE 전용 확장 설치 및 설정이 필수적임

## Compatibility / migration notes
- TBD
