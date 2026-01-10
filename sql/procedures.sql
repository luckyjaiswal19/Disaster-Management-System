-- Stored Procedures for Disaster Management System
-- Implements transaction-safe operations for critical workflows

DELIMITER //

-- Procedure 1: Process request approval with transaction and quantity deduction
CREATE PROCEDURE process_request_approval(
    IN p_request_id INT,
    IN p_admin_id INT,
    IN p_comment TEXT
)
BEGIN
    DECLARE v_resource_id INT;
    DECLARE v_quantity INT;
    DECLARE v_available_qty INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    -- Get request details
    SELECT resource_id, quantity INTO v_resource_id, v_quantity
    FROM requests 
    WHERE id = p_request_id AND status = 'Pending';
    
    IF v_resource_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Request not found or not pending';
    END IF;
    
    -- Check available quantity
    SELECT available_quantity INTO v_available_qty
    FROM resources 
    WHERE id = v_resource_id FOR UPDATE; -- Lock row for update
    
    IF v_available_qty < v_quantity THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient resource quantity';
    END IF;
    
    -- Deduct from available quantity
    UPDATE resources 
    SET available_quantity = available_quantity - v_quantity
    WHERE id = v_resource_id;
    
    -- Create admin response
    INSERT INTO admin_responses (request_id, admin_id, action, comment)
    VALUES (p_request_id, p_admin_id, 'Approved', p_comment);
    
    -- Request status updated by trigger
    
    COMMIT;
END//

-- Procedure 2: Process request rejection
CREATE PROCEDURE process_request_rejection(
    IN p_request_id INT,
    IN p_admin_id INT,
    IN p_comment TEXT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    -- Verify request exists and is pending
    IF NOT EXISTS (SELECT 1 FROM requests WHERE id = p_request_id AND status = 'Pending') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Request not found or not pending';
    END IF;
    
    -- Create admin response
    INSERT INTO admin_responses (request_id, admin_id, action, comment)
    VALUES (p_request_id, p_admin_id, 'Rejected', p_comment);
    
    -- Request status updated by trigger
    
    COMMIT;
END//

-- Procedure 3: Get resource statistics for dashboard
CREATE PROCEDURE get_resource_statistics()
BEGIN
    SELECT 
        r.category,
        COUNT(r.id) as resource_count,
        SUM(r.total_quantity) as total_quantity,
        SUM(r.available_quantity) as available_quantity,
        ROUND((SUM(r.total_quantity - r.available_quantity) / SUM(r.total_quantity)) * 100, 2) as utilization_rate
    FROM resources r
    GROUP BY r.category
    ORDER BY utilization_rate DESC;
END//

DELIMITER ;