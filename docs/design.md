## 계획

1. GM 업무 구분

# GM의 역할

- 플레이어 입력/gm 입력으로 룰 엔진에 요청
- 룰엔진 상태 변경 내용을 시나리오에 맞춰 수정
- 상태 변경 적용
- 상태 변경 결과 전달
- 상태 변경 결과 요약 서술 전달

# 업무 종류

- [] 기반시스템 구축

  - rule engine & state DB 계약 정의
  - play_log_DB 설계

- [] 핵심로직 구현

  - GM 핵심 처리루프 구현
  - Scenario DB 연계방식 확정

- [] 요약 및 서술화
  - Description LLM 연결
  - Vector DB 활용정리

1. 업무별 설계 내역

[state DB]
