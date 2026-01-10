-- Database Views for Disaster Management System
-- Provides simplified queries for common reporting needs

-- View 1: Resource availability summary with utilization
CREATE OR REPLACE VIEW resource_availability_view AS
SELECT 
    r.id,
    r.name,
    r.category,
    r.total_quantity,
    r.available_quantity,
    (r.total_quantity - r.available_quantity) as allocated_quantity,
    CASE 
        WHEN r.total_quantity > 0 THEN 
            ROUND(((r.total_quantity - r.available_quantity) / r.total_quantity) * 100, 2)
        ELSE 0 
    END as utilization_percentage,
    r.unit,
    CASE 
        WHEN r.available_quantity = 0 THEN 'Out of Stock'
        WHEN r.available_quantity < (r.total_quantity * 0.1) THEN 'Low Stock'
        WHEN r.available_quantity < (r.total_quantity * 0.3) THEN 'Medium Stock'
        ELSE 'Good Stock'
    END as stock_status
FROM resources r
ORDER BY utilization_percentage DESC;

-- View 2: Event summary with request and donation counts
CREATE OR REPLACE VIEW event_summary_view AS
SELECT 
    e.id,
    e.name,
    e.severity,
    e.status,
    e.created_at,
    COUNT(DISTINCT r.id) as total_requests,
    COUNT(DISTINCT d.id) as total_donations,
    SUM(CASE WHEN r.status = 'Pending' THEN 1 ELSE 0 END) as pending_requests,
    SUM(CASE WHEN r.status = 'Approved' THEN 1 ELSE 0 END) as approved_requests,
    SUM(d.quantity) as total_donated_quantity
FROM events e
LEFT JOIN requests r ON e.id = r.event_id
LEFT JOIN donations d ON e.id = d.event_id
GROUP BY e.id, e.name, e.severity, e.status, e.created_at
ORDER BY e.created_at DESC;

-- View 3: User activity summary
CREATE OR REPLACE VIEW user_activity_view AS
SELECT 
    u.id,
    u.name,
    u.email,
    u.is_admin,
    u.created_at,
    COUNT(DISTINCT d.id) as total_donations,
    COUNT(DISTINCT r.id) as total_requests,
    SUM(d.quantity) as total_donated_quantity,
    MAX(COALESCE(d.donated_at, r.created_at)) as last_activity
FROM users u
LEFT JOIN donations d ON u.id = d.user_id
LEFT JOIN requests r ON u.id = r.user_id
GROUP BY u.id, u.name, u.email, u.is_admin, u.created_at
ORDER BY last_activity DESC;