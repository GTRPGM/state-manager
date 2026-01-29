-- 1. 마스터 시나리오 존재 확인
SELECT scenario_id, title FROM scenario WHERE scenario_id = '00000000-0000-0000-0000-000000000000';

-- 2. 배포 시 타임스탬프 트리거 작동 확인
SELECT scenario_id, is_published, published_at FROM scenario WHERE published_at IS NOT NULL;