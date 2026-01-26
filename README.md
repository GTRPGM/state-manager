# GTRPGM State Manager

GTRPGM 프로젝트의 상태 관리(State Manager) 서비스입니다.
게임 세션, 플레이어, NPC, Enemy 등의 상태를 DB(PostgreSQL + Apache AGE)에 저장하고 관리하며, Rule Engine 및 GM Agent에 최신 상태를 제공합니다.

## 🛠️ 기술 스택

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL (with Apache AGE Extension for Graph Database)
- **Dependency Management**: `uv`
- **Testing**: `pytest`

## 🚀 시작하기

### 1. 환경 설정

`uv`가 설치되어 있어야 합니다.

```bash
# 가상환경 생성 및 의존성 설치
uv sync
```

### 2. 환경 변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 설정을 수정합니다.

```bash
cp .env.example .env
```

### 3. 데이터베이스 설정

PostgreSQL에 Apache AGE 확장이 설치되어 있어야 합니다.
데이터베이스 정보를 `.env`에 맞게 설정하세요.

### 4. 서버 실행

```bash
# 개발 모드 (Hot reload)
uv run python -m src.state_db.main

# 또는
uv run uvicorn src.state_db.main:app --reload
```

서버는 기본적으로 `http://127.0.0.1:8030`에서 실행됩니다.

## 🧪 테스트 실행

```bash
# 전체 테스트 실행
uv run pytest

# 특정 테스트 파일 실행
uv run pytest tests/test_router.py
```

## 📚 API 문서

서버 실행 후 브라우저에서 아래 주소로 접속하면 Swagger UI를 확인할 수 있습니다.

- Swagger UI: `http://127.0.0.1:8030/docs`
- ReDoc: `http://127.0.0.1:8030/redoc`

## 📁 프로젝트 구조

```bash
src/state_db/
├── configs/        # 설정 파일
├── data/           # 데이터 스키마 (Graph)
├── Query/          # SQL 쿼리 파일 및 실행기
├── custom.py       # 커스텀 응답/예외 클래스
├── main.py         # 앱 진입점
├── pipeline.py     # 상태 처리 파이프라인 (Rule Engine 연동)
├── router.py       # API 라우터
└── schemas.py      # Pydantic 데이터 모델
```
