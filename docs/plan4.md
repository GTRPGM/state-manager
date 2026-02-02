# 구현 계획: Proxy, Logger, Color Formatter

## 개요
State Manager에 마이크로서비스 프록시 모듈, 로깅 믹스인, 레벨별 색상 포매터를 추가합니다.

---

## Phase 1: 기반 설정

### 1.1 configs/setting.py 수정
**경로**: `src/state_db/configs/setting.py`

추가할 환경변수:
```python
# 마이크로서비스 프록시 설정
RULE_ENGINE_URL = os.getenv("RULE_ENGINE_URL", "http://localhost:8050")
GM_URL = os.getenv("GM_URL", "http://localhost:8020")

# 프록시 타임아웃 및 재시도 설정 | reraise 고려할것!
PROXY_TIMEOUT = float(os.getenv("PROXY_TIMEOUT", 10.0))
PROXY_MAX_RETRIES = int(os.getenv("PROXY_MAX_RETRIES", 3))
PROXY_RETRY_MIN_WAIT = float(os.getenv("PROXY_RETRY_MIN_WAIT", 1.0))
PROXY_RETRY_MAX_WAIT = float(os.getenv("PROXY_RETRY_MAX_WAIT", 10.0))
```

### 1.2 .env.example 업데이트
```env
# 마이크로서비스 프록시 설정
RULE_ENGINE_URL=http://localhost:8050
AI_GM_URL=http://localhost:8020
PROXY_TIMEOUT=10.0
PROXY_MAX_RETRIES=3
```

### 1.3 pyproject.toml - 의존성 추가
```toml
tenacity = "^8.2.0"  # 재시도 로직용
```

---

## Phase 2: 독립 기능 구현

### 2.1 schemas/mixins.py - LoggableMixin 추가
**경로**: `src/state_db/schemas/mixins.py`

기능:
- `get_log_context()`: 로깅용 컨텍스트 딕셔너리 반환
- `log_info/debug/warning/error()`: 레벨별 로깅 메서드
- `to_log_string()`: 엔티티의 로깅용 문자열 표현

```python
class LoggableMixin(BaseModel):
    """엔티티 로깅 표준화를 위한 믹스인"""

    def get_log_context(self) -> Dict[str, Any]:
        # entity_type, timestamp, ID 필드 자동 감지

    def log_info(self, message: str, logger=None, extra=None):
        # [entity_id...] [EntityType] message 형식으로 출력
```

### 2.2 color_hint_formatter.py - 레벨별 색상
**경로**: `src/state_db/configs/color_hint_formatter.py`

색상 매핑:
- DEBUG: cyan (`\033[36m`)
- INFO: green (`\033[32m`) - 기본
- WARNING: yellow (`\033[33m`)
- ERROR: red (`\033[31m`)
- CRITICAL: bright_red (`\033[91m`)

```python
class ColorHintFormatter(DefaultFormatter):
    LEVEL_COLORS = {
        logging.DEBUG: "cyan",
        logging.INFO: "green",
        logging.WARNING: "yellow",
        logging.ERROR: "red",
        logging.CRITICAL: "bright_red",
    }
```

---

## Phase 3: Proxy 코어 모듈

### 3.1 디렉토리 구조 생성
```
src/state_db/proxy/
├── __init__.py
├── client.py          # HTTPClientManager + proxy_request
└── services/
    ├── __init__.py
    ├── rule_engine.py
    └── ai_gm.py
```

### 3.2 proxy/client.py - HTTPClientManager
**패턴**: DatabaseManager 싱글톤 패턴 따름

```python
class HTTPClientManager:
    _client: Optional[httpx.AsyncClient] = None

    @classmethod
    async def get_client(cls) -> httpx.AsyncClient:
        if cls._client is None:
            cls._client = httpx.AsyncClient(
                timeout=httpx.Timeout(PROXY_TIMEOUT),
                limits=httpx.Limits(max_connections=100)
            )
        return cls._client

    @classmethod
    async def close_client(cls) -> None:
        if cls._client:
            await cls._client.aclose()
            cls._client = None
```

### 3.3 proxy_request 함수
- tenacity 재시도 데코레이터 적용
- 연결 실패 → 503 반환
- 타임아웃 → 504 반환
- 4xx/5xx → HTTPException 변환

### 3.4 infrastructure/lifecycle.py 통합
startup()에 `HTTPClientManager.get_client()` 추가
shutdown()에 `HTTPClientManager.close_client()` 추가

---

## Phase 4: 서비스별 프록시

### 4.1 proxy/services/rule_engine.py
```python
class RuleEngineProxy:
    base_url = RULE_ENGINE_URL

    @classmethod
    async def validate_action(cls, session_id, action_type, action_data, token=None)

    @classmethod
    async def calculate_outcome(cls, session_id, action_result, token=None)

    @classmethod
    async def health_check(cls)
```

### 4.2 proxy/services/ai_gm.py
```python
class AIGMProxy:
    base_url = AI_GM_URL

    @classmethod
    async def generate_narrative(cls, session_id, context, prompt_type, token=None)

    @classmethod
    async def generate_npc_response(cls, session_id, npc_id, player_action, context, token=None)

    @classmethod
    async def health_check(cls)
```

---

## 수정 파일 목록

| 작업 | 파일 경로 |
|------|----------|
| 수정 | `src/state_db/configs/setting.py` |
| 수정 | `src/state_db/configs/__init__.py` (export 추가) |
| 수정 | `src/state_db/schemas/mixins.py` |
| 수정 | `src/state_db/configs/color_hint_formatter.py` |
| 수정 | `src/state_db/infrastructure/lifecycle.py` |
| 수정 | `.env.example` |
| 수정 | `pyproject.toml` |
| 생성 | `src/state_db/proxy/__init__.py` |
| 생성 | `src/state_db/proxy/client.py` |
| 생성 | `src/state_db/proxy/services/__init__.py` |
| 생성 | `src/state_db/proxy/services/rule_engine.py` |
| 생성 | `src/state_db/proxy/services/ai_gm.py` |

---

## 검증 방법

### 1. 의존성 설치
```bash
pip install -e .  # tenacity 설치 확인
```

### 2. 서버 시작 확인
```bash
python -m state_db.main
# 로그에서 "HTTP client pool initialized" 메시지 확인
# 로그 색상이 레벨별로 다르게 표시되는지 확인
```

### 3. 프록시 헬스체크 (선택)
```bash
curl http://localhost:8030/health/proxy
```

### 4. 기존 테스트 통과 확인
```bash
pytest tests/ -v
```

---

## 구현 순서
1. setting.py + .env.example + pyproject.toml (기반)
2. color_hint_formatter.py (독립)
3. schemas/mixins.py (독립)
4. proxy/client.py (핵심)
5. infrastructure/lifecycle.py 통합
6. proxy/services/*.py (서비스별)
7. configs/__init__.py export 업데이트
