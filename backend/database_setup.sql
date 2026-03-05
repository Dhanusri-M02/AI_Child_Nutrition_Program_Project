-- Database Schema for Child Nutrition Program
-- Run this SQL in your MySQL database to set up the tables

-- Create database (if not exists)
-- CREATE DATABASE IF NOT EXISTS child_nutrition;
-- USE child_nutrition;

-- ============================================
-- USERS TABLE (with role support)
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('parent', 'nutrition_worker', 'admin') NOT NULL DEFAULT 'parent',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================
-- CHILDREN TABLE (linked to parents)
-- ============================================
CREATE TABLE IF NOT EXISTS children (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    sex ENUM('0', '1') NOT NULL,  -- 0=Female, 1=Male
    age DECIMAL(5,2) NOT NULL,
    weight DECIMAL(5,2) NOT NULL,  -- in kg
    height DECIMAL(5,2) NOT NULL,  -- in cm
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- HEALTH RECORDS TABLE (nutrition predictions)
-- ============================================
CREATE TABLE IF NOT EXISTS health_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    recorded_by INT NOT NULL,  -- nutrition_worker or parent
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
-- SAMPLE DATA (for testing)
-- ============================================
-- Insert sample users (password is 'password123' hashed with bcrypt)
-- You can add sample data after running the app

-- ============================================
-- INDEXES FOR BETTER PERFORMANCE
-- ============================================
CREATE INDEX idx_children_parent ON children(parent_id);
CREATE INDEX idx_health_records_child ON health_records(child_id);
CREATE INDEX idx_health_records_recorded_by ON health_records(recorded_by);
CREATE INDEX idx_users_role ON users(role);
