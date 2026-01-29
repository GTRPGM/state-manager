# GTRPGM 시나리오 시스템 연동 및 상태 관리 가이드 (Hand-held)

이 문서는 시나리오 서비스와 상태 관리자(State Manager) 간의 데이터 흐름, 상태 추적 방식, 그리고 시나리오 주입 규격을 정의합니다.

---

## 1. 아키텍처 개요: 템플릿 vs 인스턴스

- **시나리오 서비스 (Template Store)**: 시나리오의 '설계도'를 관리합니다. 액트(지역), 시퀀스(지점), 엔티티 템플릿의 정적인 구조를 가집니다.
- **상태 관리자 (Session Instance)**: 실제 플레이 중인 '현재 상태'를 기록합니다. 특정 세션에서 어떤 액트와 시퀀스가 활성화되어 있는지, NPC의 현재 HP는 얼마인지 등을 추적합니다.

---

## 2. 시나리오 주입 스키마 (Injection Schema)

시나리오 생성 후 상태 관리자의 템플릿 저장소로 전달되는 데이터 구조입니다.

### 계층 구조: Scenario → Act (Region) → Sequence (POI)

```json
{
  "scenario_id": "UUID",
  "title": "시나리오 제목",
  "acts": [
    {
      "id": "act-1",
      "region_name": "지역명 (예: 시작의 마을)",
      "region_description": "지역 전체에 대한 상세 묘사",
      "exit_criteria": "다음 지역으로 넘어가기 위한 대규모 이동 트리거",
      "sequences": ["seq-1", "seq-2"]
    }
  ],
  "sequences": [
    {
      "id": "seq-1",
      "location_name": "특정 지점명 (예: 광장 주점)",
      "description": "해당 지점의 상세 묘사",
      "exit_triggers": ["종료 조건 리스트"],
      "npcs": [{"scenario_npc_id": "npc-1", "master_id": "...", "state": {...}}],
      "enemies": [...],
      "items": [...]
    }
  ],
  "relations": [...]
}
```

---

## 3. 상태 추적 및 조회 프로세스

상태 관리자는 세션별로 다음 정보를 실시간으로 추적하고 조회 가능해야 합니다.

### 3.1 세션 상태 추적 (State Manager의 역할)
세션 테이블(`sessions`)은 다음의 외래키를 통해 시나리오 진행도를 관리합니다.
- `current_act_id`: 플레이어가 현재 머물고 있는 지역(Act) ID.
- `current_seq_id`: 플레이어가 현재 상호작용 중인 지점(Sequence) ID.
- `progression_flags`: 특정 목표 달성 여부를 기록하는 불리언 맵.

### 3.2 상태 조회 흐름
사용자나 GM 서비스가 "지금 어디야?"라고 물으면 상태 관리자는 다음을 조합하여 반환합니다.
1. `session.current_act_id` → 시나리오 템플릿의 `region_name` 추출.
2. `session.current_seq_id` → 시나리오 템플릿의 `location_name` 및 `description` 추출.
3. `session_entities` → 해당 시퀀스에 소속된 엔티티들의 **현재(Modified)** 상태값 추출.

---

## 4. 시나리오 전이(Transition) 동작 과정

플레이어의 행동에 따라 상태가 변하는 표준 워크플로우입니다.

1. **사용자 입력**: 플레이어가 "주점에서 나와서 광장으로 갈래"라고 입력.
2. **판정 요청 (GM → Scenario Service)**:
   - 호출: `POST /api/v1/scenario/validate-progression`
   - 전달: `scenario_id`, `current_act_id`, `current_seq_id`, `user_input`
3. **판정 결과 반환**:
   - 시나리오 서비스는 해당 액트 내의 모든 시퀀스를 대조하여 `next_seq_id="광장"`을 판정.
   - 결과: `{ "is_triggered": true, "next_seq_id": "seq-square", "suggested_narration": "..." }`
4. **상태 업데이트 (GM → State Manager)**:
   - GM은 판정 결과를 받아 상태 관리자에게 세션의 `current_seq_id`를 `seq-square`로 업데이트 요청.
5. **묘사 출력**: 업데이트된 장소의 정보와 내레이션을 플레이어에게 전달.

---

## 5. 비선형 탐색 모델 가이드

- **지역 내 이동**: 같은 `act_id` 내에서는 `next_seq_id`만 수시로 바뀝니다. (자율 탐색)
- **지역 간 이동**: `current_act.exit_criteria`가 만족될 때만 `next_act_id`가 바뀌며, 이는 대규모 서사적 전환으로 처리됩니다.
