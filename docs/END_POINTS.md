# State Manager API Reference

State Manager API 레퍼런스 문서입니다. 게임 세션의 상태 관리를 위한 모든 엔드포인트를 정리합니다.

---

## 목차

| # | 섹션 | 설명 |
|---|------|------|
| 0 | [공통 응답 형식](#공통-응답-형식) | API 응답 구조 |
| 0 | [루트 엔드포인트](#루트-엔드포인트) | 서버 상태 확인 |
| 1 | [Session & Progress](#1-session--progress) | 세션 시작/제어/조회 및 스토리 진행 관리 |
| 2 | [State Inquiry](#2-state-inquiry) | 플레이어/인벤토리/엔티티 조회 |
| 3 | [State Updates](#3-state-updates) | 플레이어/적/아이템 상태 변경 |
| 4 | [Entity Management](#4-entity-management) | NPC/적 스폰/제거/퇴장/복귀 |
| 5 | [State Commit](#5-state-commit) | GM 판정 결과 일괄 확정 |
| 6 | [TRACE - Turn History](#6-trace---turn-history) | 턴 이력 추적 및 분석 |
| 7 | [Scenario Management](#7-scenario-management) | 시나리오 조회/검증/주입 |
| 8 | [Proxy Health Check](#8-proxy-health-check) | 마이크로서비스 연결 확인 |
| - | [Error Responses](#error-responses) | 에러 응답 형식 |
| - | [Data Types Reference](#data-types-reference) | 데이터 타입 참조 |

---

## 공통 응답 형식

모든 API는 `WrappedResponse` 형식으로 응답합니다:

```json
{
  "status": "success" | "error",
  "data": { ... }
}
```

---

## 루트 엔드포인트

서버 및 DB 상태 확인용 엔드포인트입니다. (prefix 없음)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/` | 서버 연결 확인 |
| GET | `/health` | 서버 헬스체크 |
| GET | `/health/db` | DB 연결 상태 확인 |

---

## 1. Session & Progress

세션의 생명주기와 스토리 진행(Act, Sequence, Turn, Location)을 통합 관리합니다.

> Router: `router_SESSION.py` | Tags: `Session & Progress`

### 세션 생명주기

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/state/session/start` | 새 세션 시작 (Rule Engine 동기화 포함) |
| POST | `/state/session/{session_id}/end` | 세션 종료 |
| POST | `/state/session/{session_id}/pause` | 세션 일시정지 |
| POST | `/state/session/{session_id}/resume` | 세션 재개 |
| DELETE | `/state/session/{session_id}` | 세션 완전 삭제 (CASCADE) |

### 세션 정보 조회

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/sessions` | 전체 세션 목록 |
| GET | `/state/sessions/active` | 활성 세션 목록 |
| GET | `/state/session/{session_id}` | 특정 세션 상세 정보 |
| GET | `/state/session/{session_id}/context` | GM용 통합 컨텍스트 조회 (인벤토리+관계+엔티티) |

### 진행 관리

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/session/{session_id}/progress` | 전체 진행률 및 상태 조회 |
| PUT | `/state/session/{session_id}/location` | 위치 업데이트 |
| POST | `/state/session/{session_id}/turn/add` | 턴 강제 증가 |
| GET | `/state/session/{session_id}/turn` | 현재 턴 정보 조회 |
| PUT | `/state/session/{session_id}/act` | Act 변경 (Cypher 기반) |
| PUT | `/state/session/{session_id}/sequence` | Sequence 변경 (Cypher 기반) |
| GET | `/state/session/{session_id}/sequence/details` | 현재 시퀀스 상세 (엔티티 포함) |

---

## 2. State Inquiry

플레이어, 인벤토리, 시나리오, NPC, 적(Enemy) 등 게임 상태를 조회합니다.

> Router: `router_INQUIRY.py` | Tags: `State Inquiry`

### 시나리오 조회

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/scenarios` | 전체 시나리오 목록 |
| GET | `/state/scenario/{scenario_id}` | 특정 시나리오 상세 |

### 플레이어 및 인벤토리 조회

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/player/{player_id}` | 플레이어 전체 상태 조회 |
| GET | `/state/session/{session_id}/inventory` | 인벤토리 목록 조회 (Cypher 기반) |
| GET | `/state/session/{session_id}/items` | 세션 아이템 목록 조회 (Cypher 기반) |

### 엔티티 조회

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/session/{session_id}/npcs` | NPC 목록 조회 (Cypher 기반) |
| GET | `/state/session/{session_id}/enemies` | 적 목록 조회 (Cypher 기반, `active_only` 파라미터) |

---

## 3. State Updates

플레이어, 적, 인벤토리, NPC 호감도, 아이템 등 게임 상태를 변경합니다.

> Router: `router_UPDATE.py` | Tags: `State Updates`

### 플레이어 상태

| Method | Endpoint | 설명 |
|--------|----------|------|
| PUT | `/state/player/{player_id}/hp` | HP 변경 (양수: 회복, 음수: 피해, 0~100 클램핑) |
| PUT | `/state/player/{player_id}/stats` | 스탯 변경 (STR/DEX/INT/LUX 등) |

### 인벤토리 및 아이템

| Method | Endpoint | 설명 |
|--------|----------|------|
| PUT | `/state/inventory/update` | 인벤토리 수량 변경 |
| POST | `/state/player/item/earn` | 아이템 획득 (Cypher 기반) |
| POST | `/state/player/item/use` | 아이템 사용 (Cypher 기반) |

### NPC 호감도

| Method | Endpoint | 설명 |
|--------|----------|------|
| PUT | `/state/npc/affinity` | NPC 호감도 변경 (Cypher 기반) |

### 적(Enemy) 상태

| Method | Endpoint | 설명 |
|--------|----------|------|
| PUT | `/state/enemy/{enemy_id}/hp` | 적 HP 변경 (SQL + Cypher 동기화) |
| POST | `/state/enemy/{enemy_id}/defeat` | 적 격파 처리 (SQL + Cypher 동기화) |

---

## 4. Entity Management

세션 내 NPC와 적(Enemy)의 생성, 삭제, 퇴장, 복귀를 관리합니다.

> Router: `router_MANAGE.py` | Tags: `Session Management`

### 적(Enemy) 관리

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/state/session/{session_id}/enemy/spawn` | 적 스폰 (SQL + Graph 동기화) |
| DELETE | `/state/session/{session_id}/enemy/{enemy_id}` | 적 제거 (SQL + Graph 동기화) |

### NPC 관리

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/state/session/{session_id}/npc/spawn` | NPC 스폰 (SQL + Graph 동기화) |
| DELETE | `/state/session/{session_id}/npc/{npc_id}` | NPC 완전 제거 (SQL + Graph 동기화) |
| POST | `/state/session/{session_id}/npc/{npc_id}/depart` | NPC 퇴장 (Soft Delete) |
| POST | `/state/session/{session_id}/npc/{npc_id}/return` | NPC 복귀 |

---

## 5. State Commit

GM의 판정 결과를 일괄적으로 반영합니다. (Batch Update)

> Router: `router_COMMIT.py` | Tags: `State Commit`

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/state/commit` | 다수 엔티티의 변경사항 일괄 확정 (턴 증가 포함) |

### 요청 형식

```json
{
  "turn_id": "{session_id}:{sequence}",
  "update": {
    "diffs": [
      {
        "state_entity_id": "player",
        "diff": { "hp": -5, "location": "market" }
      }
    ],
    "relations": [
      {
        "cause_entity_id": "npc-1",
        "effect_entity_id": "enemy-1",
        "type": "적대적",
        "affinity_score": -20
      }
    ]
  }
}
```

---

## 6. TRACE - Turn History

턴 진행 이력을 추적하고 분석합니다. 리플레이 및 디버깅에 활용됩니다.

> Router: `router_TRACE.py` | Tags: `TRACE - Turn History`

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/session/{session_id}/turns` | 전체 턴 이력 |
| GET | `/state/session/{session_id}/turns/recent` | 최근 N개 턴 (`limit` 파라미터, 기본 10) |
| GET | `/state/session/{session_id}/turn/latest` | 가장 최근 턴 |
| GET | `/state/session/{session_id}/turn/{turn_number}` | 특정 턴 상세 |
| GET | `/state/session/{session_id}/turns/range` | 턴 범위 조회 (`start`, `end` 파라미터) |
| GET | `/state/session/{session_id}/turns/statistics/by-type` | Turn Type별 집계 |
| GET | `/state/session/{session_id}/turns/duration-analysis` | 턴 소요시간 분석 |
| GET | `/state/session/{session_id}/turns/summary` | 턴 요약 리포트 |

---

## 7. Scenario Management

시나리오 데이터를 검증하고 SQL + Graph DB에 주입합니다.

> Router: `router_SCENARIO.py` | Tags: `Scenario Management` | Prefix: `/state/scenario`

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/scenario/list` | 시나리오 목록 조회 |
| POST | `/state/scenario/validate` | 시나리오 데이터 사전 검증 (GraphValidator) |
| POST | `/state/scenario/inject` | 시나리오 주입 (SQL + Graph DB) |

---

## 8. Proxy Health Check

외부 마이크로서비스(Rule Engine, GM)와의 연결 상태를 확인합니다.

> Router: `router_PROXY.py` | Tags: `Proxy`

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/health/proxy` | 전체 프록시 연결 상태 (Rule Engine + GM) |
| GET | `/state/health/proxy/rule-engine` | Rule Engine 연결 확인 |
| GET | `/state/health/proxy/gm` | GM 서비스 연결 확인 |

---

## Error Responses

| 상태 코드 | 설명 |
|-----------|------|
| 400 | Bad Request (잘못된 요청 형식, 유효하지 않은 ID 등) |
| 404 | Not Found (세션/플레이어/엔티티 미발견) |
| 422 | Validation Error (Pydantic 스키마 검증 실패) |
| 500 | Internal Server Error (DB 오류, 서버 내부 오류) |

---

## Data Types Reference

| 타입 | 설명 |
|------|------|
| UUID | 대부분의 ID 필드 (세션, 플레이어, NPC, 적, 아이템 등) |
| Timestamp | ISO 8601 형식 (UTC) |
| SessionStatus | `active` / `paused` / `ended` |

---

## 엔드포인트 요약

| 라우터 | 엔드포인트 수 | 주요 기능 |
|--------|:---:|------|
| SESSION | 16 | 세션 생명주기 + 진행 관리 (Act/Sequence/Turn/Location) |
| INQUIRY | 7 | 읽기 전용 조회 (시나리오/플레이어/인벤토리/NPC/적) |
| UPDATE | 8 | 상태 갱신 (HP/스탯/인벤토리/호감도/적 HP/아이템) |
| MANAGE | 6 | 엔티티 관리 (NPC/적 스폰/제거/퇴장/복귀) |
| COMMIT | 1 | GM 판정 결과 일괄 커밋 |
| TRACE | 8 | 턴 이력/통계/분석 |
| SCENARIO | 3 | 시나리오 목록/검증/주입 |
| PROXY | 3 | 마이크로서비스 헬스체크 |
| **루트** | **3** | **서버/DB 헬스체크** |
| **합계** | **55** | |

---

## 수정 이력

| 날짜 | 내용 |
|------|------|
| 2026-02-05 | Phase 시스템 제거 반영 및 라우터 구조 재구성(Session 통합) |
| 2026-02-07 | 전체 재작성: 8개 라우터 55개 엔드포인트 완전 반영, Cypher 기반 조회 명시, HP 클램핑(0~100) 반영 |
