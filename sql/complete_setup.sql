-- Disaster Management System - Complete Setup
SET FOREIGN_KEY_CHECKS=0;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS admin_responses, donations, requests, resources, events, users;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_admin (is_admin)
);

-- Events table
CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    severity ENUM('Low', 'Medium', 'High', 'Critical') DEFAULT 'Medium',
    status ENUM('Active', 'Resolved', 'Archived') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_location (latitude, longitude)
);

-- Resources table
CREATE TABLE resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    total_quantity INT DEFAULT 0,
    available_quantity INT DEFAULT 0,
    unit VARCHAR(20) DEFAULT 'units',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_category (category)
);

-- Donations table
CREATE TABLE donations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    resource_id INT NOT NULL,
    event_id INT,
    quantity INT NOT NULL,
    status ENUM('Pending', 'Completed', 'Cancelled') DEFAULT 'Completed',
    donated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_resource_id (resource_id)
);

-- Requests table
CREATE TABLE requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    resource_id INT NOT NULL,
    event_id INT NOT NULL,
    quantity INT NOT NULL,
    urgency ENUM('Low', 'Medium', 'High', 'Critical') DEFAULT 'Medium',
    status ENUM('Pending', 'Approved', 'Rejected', 'Fulfilled') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);

-- Admin responses table
CREATE TABLE admin_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL,
    admin_id INT NOT NULL,
    action ENUM('Approved', 'Rejected') NOT NULL,
    comment TEXT,
    responded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES requests(id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_request_id (request_id)
);

SET FOREIGN_KEY_CHECKS=1;

-- Insert sample data
INSERT INTO users (name, email, phone, password_hash, is_admin) VALUES
('Admin User', 'admin@disaster.org', '+1234567890', '$2b$12$LQv3c1yqBNWR1FcHZLkOC.AWvW5jLc6RgVK9k7R8QnYZN7QY8Y8XK', TRUE),
('John Doe', 'john@example.com', '+1234567891', '$2b$12$LQv3c1yqBNWR1FcHZLkOC.AWvW5jLc6RgVK9k7R8QnYZN7QY8Y8XK', FALSE),
('Jane Smith', 'jane@example.com', '+1234567892', '$2b$12$LQv3c1yqBNWR1FcHZLkOC.AWvW5jLc6RgVK9k7R8QnYZN7QY8Y8XK', FALSE);

INSERT INTO events (name, description, latitude, longitude, severity, status) VALUES
('Hurricane Relief - Florida', 'Major hurricane causing widespread damage', 27.6648, -81.5158, 'High', 'Active'),
('Earthquake Response - California', '7.2 magnitude earthquake', 36.7783, -119.4179, 'Critical', 'Active');

INSERT INTO resources (name, category, description, total_quantity, available_quantity, unit) VALUES
('Bottled Water', 'Food', 'Clean drinking water', 1000, 850, 'bottles'),
('Emergency Blankets', 'Shelter', 'Thermal emergency blankets', 500, 500, 'units'),
('First Aid Kits', 'Medical', 'Basic medical supplies', 200, 180, 'kits'),
('Canned Food', 'Food', 'Non-perishable canned goods', 800, 750, 'cans');

INSERT INTO donations (user_id, resource_id, event_id, quantity, notes) VALUES
(2, 1, 1, 50, 'Water donation for hurricane victims'),
(3, 3, 2, 10, 'First aid kits for earthquake response');

INSERT INTO requests (user_id, resource_id, event_id, quantity, urgency, status) VALUES
(2, 1, 1, 20, 'High', 'Pending'),
(3, 3, 2, 5, 'Medium', 'Pending');