# Backend Proxy 작업 계획서

## 현재 상황 요약

### 완료된 작업
- **State Manager API 완성**: 43개 엔드포인트 100% 테스트 통과
- **리팩터링 완료**: 대형 파일 분할, SQL 파라미터 표준화($1, $2)
- **주요 기능 구현 완료**:
  - 세션 생명주기 관리 (start/end/pause/resume)
  - Phase/Turn 관리
  - Act/Sequence 스토리 진행
  - Player/NPC/Enemy 상태 관리
  - 인벤토리 시스템
  - TRACE 이력 추적
  - 시나리오 데이터 주입

### 현재 아키텍처
```
[Client/Frontend]
       ↓
[State Manager (FastAPI)] ← 현재 위치
       ↓
[PostgreSQL + Apache AGE]
```

---

## 프록시 작성 목적

다른 마이크로서비스(Rule Engine, AI GM 등)와의 통신을 위한 **공통 프록시 레이어** 구축

### 예상 아키텍처
```
[Client/Frontend]
       ↓
[API Gateway 또는 State Manager]
       ↓ (프록시)
┌──────┼──────┐
↓      ↓      ↓
[State] [Rule] [AI GM]
Manager Engine  Service
```

---

## 프록시 코드 분석

제공된 프록시 코드 (`proxy_request` 함수)의 구조:

```python
async def proxy_request(method: str, base_url: str, path: str, token: str, params=None, json=None):
    """마이크로서비스로 요청을 전달하는 공통 비동기 메서드"""
```

### 주요 기능
| 기능 | 구현 방식 |
|------|-----------|
| HTTP 클라이언트 | `httpx.AsyncClient` (비동기) |
| 인증 | Bearer 토큰 헤더 주입 |
| 타임아웃 | 10초 고정 |
| 에러 처리 | 4xx/5xx → HTTPException 변환 |
| 연결 실패 | 503 Service Unavailable 반환 |

---

## 작업 시 고려사항

### 1. 설정 관리 (configs/setting.py 확장)

```python
# 추가할 환경변수
RULE_ENGINE_URL = os.getenv("RULE_ENGINE_URL", "http://localhost:8031")
AI_GM_URL = os.getenv("AI_GM_URL", "http://localhost:8032")
PROXY_TIMEOUT = float(os.getenv("PROXY_TIMEOUT", 10.0))
```

### 2. 파일 구조 제안

```
src/state_db/
├── proxy/                    # 새로 추가
│   ├── __init__.py
│   ├── client.py            # 공통 프록시 클라이언트
│   └── services/
│       ├── __init__.py
│       ├── rule_engine.py   # Rule Engine 전용 프록시
│       └── ai_gm.py         # AI GM 전용 프록시
```

### 3. 커넥션 풀링 고려

현재 코드는 매 요청마다 `AsyncClient`를 생성/종료:
```python
async with httpx.AsyncClient() as client:  # 매번 새로 생성
```

**개선안**: 앱 시작 시 클라이언트 생성, lifespan에서 관리
```python
# main.py의 lifespan에 추가
app.state.http_client = httpx.AsyncClient(timeout=10.0)
# 종료 시
await app.state.http_client.aclose()
```

### 4. 재시도 로직 (옵션)

네트워크 일시적 실패 대응:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def proxy_request_with_retry(...):
    ...
```

### 5. 인증 토큰 흐름

현재 State Manager에는 인증 시스템이 없음. 고려할 옵션:
- **옵션 A**: 프록시 호출 시 클라이언트에서 토큰 전달
- **옵션 B**: 서비스 간 내부 통신용 고정 API Key 사용
- **옵션 C**: JWT 토큰 검증 미들웨어 추가 (schemas/auth.py 존재)

### 6. 에러 응답 표준화

BE_operation.md의 "예외 응답 표준화" 원칙 적용:
```json
{
  "status": "error",
  "code": "RULE_ENGINE_UNAVAILABLE",
  "message": "Rule Engine 서비스에 연결할 수 없습니다.",
  "detail": "Connection timeout after 10s"
}
```

---

## 작업 순서 (체크리스트)

### Phase 1: 기반 구축
- [ ] `src/state_db/proxy/` 디렉터리 생성
- [ ] `configs/setting.py`에 마이크로서비스 URL 환경변수 추가
- [ ] `proxy/client.py`에 공통 프록시 함수 작성
- [ ] 커넥션 풀링 적용 (lifespan 연동)

### Phase 2: 서비스별 프록시 구현
- [ ] Rule Engine 프록시 (`proxy/services/rule_engine.py`)
- [ ] AI GM 프록시 (`proxy/services/ai_gm.py`)
- [ ] 필요 시 추가 서비스 프록시

### Phase 3: 라우터 연동
- [ ] 프록시를 호출하는 새 라우터 추가 또는 기존 라우터에서 호출
- [ ] 의존성 주입(Dependency Injection) 패턴 적용

### Phase 4: 테스트 및 검증
- [ ] 단위 테스트: Mock을 이용한 프록시 함수 테스트
- [ ] 통합 테스트: 실제 서비스 연동 테스트
- [ ] Docker Compose 환경에서 멀티 서비스 테스트

---

## 다음 단계 (프록시 이후)

1. **인증/인가 시스템 구축**
   - JWT 토큰 검증 미들웨어
   - API Key 관리 (schemas/auth.py 활용)

2. **서비스 간 통신 프로토콜 정의**
   - Rule Engine ↔ State Manager 인터페이스
   - AI GM ↔ State Manager 인터페이스

3. **모니터링 및 로깅**
   - 프록시 요청/응답 로깅
   - 서비스 헬스체크 대시보드

4. **Circuit Breaker 패턴 (선택)**
   - 서비스 장애 시 빠른 실패 처리
   - 자동 복구 감지

---

## 참고 문서

- [BE_operation.md](./BE_operation.md): HTTP 통신 흐름 및 이론
- [END_POINTS.md](./END_POINTS.md): State Manager API 레퍼런스
- [current_task.md](./current_task.md): 현재 완료된 작업 내역

---

## 수정 이력

| 날짜 | 내용 |
|------|------|
| 2026-02-01 | 초기 문서 작성 |
