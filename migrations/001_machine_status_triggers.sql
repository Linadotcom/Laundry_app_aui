-- ============================================================
-- MIGRATION 001: Machine status auto-sync triggers
-- Date: 2026-05-08
-- Purpose: Keep Laundry_Machine.current_status in sync with
--          Laundry_Order whenever orders are updated via SQL
--          or the web app. INSERT is already handled by the
--          existing trg_machine_start trigger.
-- ============================================================


-- ── FUNCTION 1: Set machine BUSY on order update ─────────────

CREATE OR REPLACE FUNCTION sync_machine_busy()
RETURNS TRIGGER AS $$
BEGIN
    -- Fire when an order is assigned to a machine via UPDATE
    IF NEW.machine_id IS NOT NULL
       AND NEW.order_status IN ('Pending', 'In Progress')
       AND (OLD.machine_id IS DISTINCT FROM NEW.machine_id
            OR OLD.order_status IS DISTINCT FROM NEW.order_status) THEN

        UPDATE Laundry_Machine
        SET current_status = 'Busy'
        WHERE machine_id = NEW.machine_id
          AND current_status != 'Maintenance';

    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS trg_sync_machine_busy ON Laundry_Order;

CREATE TRIGGER trg_sync_machine_busy
AFTER UPDATE OF machine_id, order_status ON Laundry_Order
FOR EACH ROW
EXECUTE FUNCTION sync_machine_busy();


-- ── FUNCTION 2: Set machine AVAILABLE when order finishes ────

CREATE OR REPLACE FUNCTION sync_machine_available()
RETURNS TRIGGER AS $$
DECLARE
    v_machine_id INTEGER;
    v_remaining  INTEGER;
BEGIN
    -- Case A: order status changed to a terminal state
    IF NEW.order_status IN ('Completed', 'Picked Up')
       AND OLD.order_status NOT IN ('Completed', 'Picked Up')
       AND NEW.machine_id IS NOT NULL THEN

        v_machine_id := NEW.machine_id;

        SELECT COUNT(*) INTO v_remaining
        FROM Laundry_Order
        WHERE machine_id = v_machine_id
          AND order_status IN ('Pending', 'In Progress')
          AND order_id != NEW.order_id;

        IF v_remaining = 0 THEN
            UPDATE Laundry_Machine
            SET current_status = 'Available'
            WHERE machine_id = v_machine_id
              AND current_status != 'Maintenance';
        END IF;
    END IF;

    -- Case B: machine_id was cleared (order unassigned)
    IF OLD.machine_id IS NOT NULL AND NEW.machine_id IS NULL THEN

        v_machine_id := OLD.machine_id;

        SELECT COUNT(*) INTO v_remaining
        FROM Laundry_Order
        WHERE machine_id = v_machine_id
          AND order_status IN ('Pending', 'In Progress');

        IF v_remaining = 0 THEN
            UPDATE Laundry_Machine
            SET current_status = 'Available'
            WHERE machine_id = v_machine_id
              AND current_status != 'Maintenance';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS trg_sync_machine_available ON Laundry_Order;

CREATE TRIGGER trg_sync_machine_available
AFTER UPDATE OF machine_id, order_status ON Laundry_Order
FOR EACH ROW
EXECUTE FUNCTION sync_machine_available();


-- ── VERIFY ───────────────────────────────────────────────────

SELECT trigger_name, event_manipulation
FROM information_schema.triggers
WHERE event_object_table = 'laundry_order'
ORDER BY trigger_name;
