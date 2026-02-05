# State Manager API Reference

State Manager API 레퍼런스 문서입니다. 게임 세션의 상태 관리를 위한 모든 엔드포인트를 정리합니다.

---

## 목차

| # | 섹션 | 설명 |
|---|------|------|
| 0 | [공통 응답 형식](#공통-응답-형식) | API 응답 구조 |
| 1 | [Session & Progress](#1-session--progress) | 세션 시작/제어/조회 및 스토리 진행 관리 |
| 2 | [Player State](#2-player-state) | 플레이어 상태 관리 |
| 3 | [Inventory Management](#3-inventory-management) | 인벤토리 관리 |
| 4 | [Entity Management](#4-entity-management) | NPC 및 적(Enemy) 관리 |
| 5 | [State Commit](#5-state-commit) | GM 판정 결과 일괄 확정 |
| 6 | [TRACE - Turn History](#6-trace---turn-history) | 턴 이력 추적 및 분석 |
| 7 | [Scenario Management](#7-scenario-management) | 시나리오 조회 및 주입 |
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

## 1. Session & Progress

세션의 생명주기와 스토리 진행(Act, Sequence, Turn, Location)을 통합 관리합니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/state/session/start` | 새 세션 시작 |
| POST | `/state/session/{session_id}/end` | 세션 종료 |
| POST | `/state/session/{session_id}/pause` | 세션 일시정지 |
| POST | `/state/session/{session_id}/resume` | 세션 재개 |
| DELETE | `/state/session/{session_id}` | 세션 완전 삭제 |
| GET | `/state/sessions` | 전체 세션 목록 |
| GET | `/state/session/{session_id}` | 특정 세션 상세 정보 |
| GET | `/state/session/{session_id}/context` | GM용 통합 컨텍스트 조회 |
| GET | `/state/session/{session_id}/progress` | 전체 진행률 및 상태 조회 |
| PUT | `/state/session/{session_id}/location` | 위치 업데이트 |
| POST | `/state/session/{session_id}/turn/add` | 턴 강제 증가 |
| GET | `/state/session/{session_id}/turn` | 현재 턴 정보 조회 |
| PUT | `/state/session/{session_id}/act` | Act 변경 |
| PUT | `/state/session/{session_id}/sequence` | Sequence 변경 |
| GET | `/state/session/{session_id}/sequence/details` | 현재 시퀀스 상세 (엔티티 포함) |

---

## 2. Player State

플레이어의 HP, 스탯, 정신력(SAN) 등 상태를 관리합니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/player/{player_id}` | 플레이어 전체 상태 조회 |
| PUT | `/state/player/{player_id}/hp` | HP 변경 (양수: 회복, 음수: 피해) |

---

## 3. Inventory Management

플레이어 인벤토리 및 아이템 획득/사용을 관리합니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/session/{session_id}/inventory` | 인벤토리 목록 조회 |
| POST | `/state/player/item/earn` | 아이템 획득 |
| POST | `/state/player/item/use` | 아이템 사용 |

---

## 4. Entity Management

세션 내 NPC와 적(Enemy)의 생성, 삭제, 수치 업데이트를 관리합니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/session/{session_id}/npcs` | NPC 목록 조회 |
| GET | `/state/session/{session_id}/enemies` | 적 목록 조회 |
| POST | `/state/session/{session_id}/npc/spawn` | NPC 스폰 |
| POST | `/state/session/{session_id}/enemy/spawn` | 적 스폰 |
| PUT | `/state/enemy/{enemy_instance_id}/hp` | 적 HP 변경 |
| PUT | `/state/npc/affinity` | NPC 호감도 변경 |
| POST | `/state/session/{session_id}/npc/{npc_id}/depart` | NPC 퇴장 (Soft Delete) |
| POST | `/state/session/{session_id}/npc/{npc_id}/return` | NPC 복귀 |

---

## 5. State Commit

GM의 판정 결과를 일괄적으로 반영합니다. (Barch Update)

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/state/commit` | 다수 엔티티의 변경사항 일괄 확정 |

---

## 6. TRACE - Turn History

턴 진행 이력을 추적하고 분석합니다. 리플레이 및 디버깅에 활용됩니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/session/{session_id}/turns` | 전체 턴 이력 |
| GET | `/state/session/{session_id}/turns/recent` | 최근 N개 턴 |
| GET | `/state/session/{session_id}/turn/latest` | 가장 최근 턴 |
| GET | `/state/session/{session_id}/turn/{turn_number}` | 특정 턴 상세 |

---

## 7. Scenario Management

시나리오 메타데이터 조회 및 초기 데이터 주입을 관리합니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/scenarios` | 전체 시나리오 목록 |
| GET | `/state/scenario/{scenario_id}` | 특정 시나리오 상세 |
| POST | `/state/scenario/inject` | 시나리오 데이터 주입 |

---

## 8. Proxy Health Check

외부 마이크로서비스(Rule Engine 등)와의 연결 상태를 확인합니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/proxy/health/rule-engine` | Rule Engine 연결 확인 |

---

## Error Responses

| 상태 코드 | 설명 |
|-----------|------|
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Data Types Reference

| 타입 | 설명 |
|------|------|
| UUID | 대부분의 ID 필드 |
| Timestamp | ISO 8601 형식 (UTC) |

---

## 수정 이력

| 날짜 | 내용 |
|------|------|
| 2026-02-05 | Phase 시스템 제거 반영 및 라우터 구조 재구성(Session 통합) |
