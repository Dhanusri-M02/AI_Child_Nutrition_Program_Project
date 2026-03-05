

-- ============================================
-- DROP AND RECREATE TABLES
-- WARNING: This will DELETE all existing data!
-- ============================================

-- First, disable foreign key checks
SET FOREIGN_KEY_CHECKS = 0;

-- Drop existing tables (in reverse order due to foreign keys)
DROP TABLE IF EXISTS health_records;
DROP TABLE IF EXISTS children;
DROP TABLE IF EXISTS users;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- RECREATE USERS TABLE
-- ============================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('parent', 'nutrition_worker', 'admin') NOT NULL DEFAULT 'parent',
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================
-- RECREATE CHILDREN TABLE
-- ============================================
CREATE TABLE children (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    sex ENUM('0', '1') NOT NULL,
    age DECIMAL(5,2) NOT NULL,
    weight DECIMAL(5,2) NOT NULL,
    height DECIMAL(5,2) NOT NULL,
    date_of_birth DATE,
    birth_weight DECIMAL(5,2),
    birth_height DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- RECREATE HEALTH RECORDS TABLE
-- ============================================
CREATE TABLE health_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    recorded_by INT NOT NULL,
    sex ENUM('0', '1') NOT NULL,
    age DECIMAL(5,2) NOT NULL,
    weight DECIMAL(5,2) NOT NULL,
    height DECIMAL(5,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    advice TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- ADD INDEXES
-- ============================================
CREATE INDEX idx_children_parent ON children(parent_id);


