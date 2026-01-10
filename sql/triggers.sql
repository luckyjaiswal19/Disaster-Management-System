-- Database Triggers for Disaster Management System
-- Ensures data consistency and automatic quantity updates

DELIMITER //

-- Trigger 1: Update resource quantities after donation insertion
CREATE TRIGGER after_donation_insert
AFTER INSERT ON donations
FOR EACH ROW
BEGIN
    -- Update both total and available quantities when donation is completed
    IF NEW.status = 'Completed' THEN
        UPDATE resources 
        SET total_quantity = total_quantity + NEW.quantity,
            available_quantity = available_quantity + NEW.quantity
        WHERE id = NEW.resource_id;
    END IF;
END//

-- Trigger 2: Validate request quantity before insertion and log insufficient resources
CREATE TRIGGER before_request_insert
BEFORE INSERT ON requests
FOR EACH ROW
BEGIN
    DECLARE available_qty INT;
    
    -- Check available quantity
    SELECT available_quantity INTO available_qty
    FROM resources 
    WHERE id = NEW.resource_id;
    
    -- Log warning if insufficient resources (for monitoring)
    IF available_qty < NEW.quantity THEN
        INSERT INTO system_logs (message, log_level, created_at) 
        VALUES (CONCAT('Insufficient resources for request: Resource ', NEW.resource_id, 
                      ', Available: ', available_qty, ', Requested: ', NEW.quantity),
               'WARNING', NOW());
    END IF;
END//

-- Trigger 3: Update request status when admin responds
CREATE TRIGGER after_admin_response_insert
AFTER INSERT ON admin_responses
FOR EACH ROW
BEGIN
    -- Update request status based on admin action
    UPDATE requests 
    SET status = 
        CASE 
            WHEN NEW.action = 'Approved' THEN 'Approved'
            WHEN NEW.action = 'Rejected' THEN 'Rejected'
        END,
        updated_at = NOW()
    WHERE id = NEW.request_id;
END//

-- System logs table for trigger logging (if not exists)
CREATE TABLE IF NOT EXISTS system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message TEXT NOT NULL,
    log_level ENUM('INFO', 'WARNING', 'ERROR') DEFAULT 'INFO',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_level (log_level),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4//

DELIMITER ;