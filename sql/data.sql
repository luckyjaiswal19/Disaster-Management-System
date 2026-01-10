-- Sample data for Disaster Management System
-- Includes users, events, resources, and initial relationships

-- Users (password is 'password123' for all users, hashed with bcrypt)
INSERT INTO users (name, email, phone, password_hash, is_admin) VALUES
('Admin User', 'admin@disaster.org', '+1234567890', '$2b$12$LQv3c1yqBNWR1FcHZLkOC.AWvW5jLc6RgVK9k7R8QnYZN7QY8Y8XK', TRUE),
('John Doe', 'john@example.com', '+1234567891', '$2b$12$LQv3c1yqBNWR1FcHZLkOC.AWvW5jLc6RgVK9k7R8QnYZN7QY8Y8XK', FALSE),
('Jane Smith', 'jane@example.com', '+1234567892', '$2b$12$LQv3c1yqBNWR1FcHZLkOC.AWvW5jLc6RgVK9k7R8QnYZN7QY8Y8XK', FALSE);

-- Events (real disaster locations)
INSERT INTO events (name, description, latitude, longitude, severity, status) VALUES
('Hurricane Relief - Florida', 'Major hurricane causing widespread damage and flooding in coastal areas', 27.6648, -81.5158, 'High', 'Active'),
('Earthquake Response - California', '7.2 magnitude earthquake affecting urban and rural communities', 36.7783, -119.4179, 'Critical', 'Active'),
('Wildfire Support - Oregon', 'Large-scale wildfires threatening residential areas and wildlife', 43.8041, -120.5542, 'Medium', 'Active');

-- Resources
INSERT INTO resources (name, category, description, total_quantity, available_quantity, unit) VALUES
('Bottled Water', 'Food', 'Clean drinking water in 500ml bottles', 1000, 850, 'bottles'),
('Emergency Blankets', 'Shelter', 'Thermal emergency blankets for warmth', 500, 500, 'units'),
('First Aid Kits', 'Medical', 'Basic medical supplies for emergency care', 200, 180, 'kits'),
('Canned Food', 'Food', 'Non-perishable canned goods', 800, 750, 'cans'),
('Tents', 'Shelter', '4-person emergency tents', 100, 95, 'units'),
('Medical Masks', 'Medical', 'Disposable protective masks', 2000, 1950, 'pieces');

-- Sample donations
INSERT INTO donations (user_id, resource_id, event_id, quantity, notes) VALUES
(2, 1, 1, 50, 'Water donation for hurricane victims'),
(3, 3, 2, 10, 'First aid kits for earthquake response'),
(2, 4, 1, 100, 'Food supplies for affected families');

-- Sample requests
INSERT INTO requests (user_id, resource_id, event_id, quantity, urgency, status) VALUES
(2, 1, 1, 20, 'High', 'Pending'),
(3, 3, 2, 5, 'Medium', 'Pending'),
(2, 4, 1, 30, 'Low', 'Approved');

-- Sample admin responses
INSERT INTO admin_responses (request_id, admin_id, action, comment) VALUES
(3, 1, 'Approved', 'Request approved. Resources will be delivered within 24 hours.');