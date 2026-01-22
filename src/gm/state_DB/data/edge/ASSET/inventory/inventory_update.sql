-- inventory_updated.sql
-- GM 명령(command_type)에 따라 session/player_inventory 상태를 업데이트
-- 기존 cypher 파일은 그대로 두고, 상태 테이블/edge를 직접 참조

DO $$
BEGIN
    -- -----------------------
    -- EARN 명령 처리
    -- -----------------------
    IF command_type = 'earn' THEN
        -- player_inventory 상태 조회/갱신
        UPDATE player_inventory
        SET active = TRUE
        WHERE player_id = :player_id
          AND session_id = :session_id;

        -- earn_item edge 활성화
        UPDATE earn_item_edge
        SET active = TRUE,
            updated_at = NOW()
        WHERE player_inventory_id IN (
            SELECT player_inventory_id
            FROM player_inventory
            WHERE player_id = :player_id
              AND session_id = :session_id
        )
        AND item_id = :item_id;

    -- -----------------------
    -- USE 명령 처리
    -- -----------------------
    ELSIF command_type = 'use' THEN
        -- used_item edge 생성/기록
        INSERT INTO used_item_edge (
            id, session_id, player_inventory_id, item_id, rule_id, created_at, success
        )
        SELECT
            gen_random_uuid(),
            :session_id,
            pi.player_inventory_id,
            :item_id,
            :rule_id,
            NOW(),
            TRUE
        FROM player_inventory pi
        WHERE pi.player_id = :player_id
          AND pi.session_id = :session_id;

        -- 사용 후 earn_item edge 제거
        DELETE FROM earn_item_edge
        WHERE item_id = :item_id
          AND session_id = :session_id
          AND player_inventory_id IN (
              SELECT player_inventory_id
              FROM player_inventory
              WHERE player_id = :player_id
                AND session_id = :session_id
          );

    -- -----------------------
    -- UPDATE 명령 처리
    -- -----------------------
    ELSIF command_type = 'update' THEN
        -- item meta 업데이트
        UPDATE item
        SET meta = meta || :meta
        WHERE item_id = :item_id
          AND session_id = :session_id;

    ELSE
        RAISE NOTICE 'Unsupported command_type: %', command_type;
    END IF;
END;
$$ LANGUAGE plpgsql;
