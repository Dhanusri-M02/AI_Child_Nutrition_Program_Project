
-- ============================================
-- ALTER EXISTING TABLES 
-- Run this if your tables already exist
-- ============================================

-- ============================================
-- 1. ALTER USERS TABLE - Add role column
-- ============================================
-- Add role column if it doesn't exist
ALTER TABLE users ADD COLUMN IF NOT EXISTS role ENUM('parent', 'nutrition_worker', 'admin') NOT NULL DEFAULT 'parent';

-- Add phone column
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20);

-- Add is_active column
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;


-- ============================================
-- 2. ALTER CHILDREN TABLE - Add new columns
-- ============================================
-- Add date_of_birth if not exists
ALTER TABLE children ADD COLUMN IF NOT EXISTS date_of_birth DATE;

-- Add birth_weight
ALTER TABLE children ADD COLUMN IF NOT EXISTS birth_weight DECIMAL(5,2);

-- Add birth_height
ALTER TABLE children ADD COLUMN IF NOT EXISTS birth_height DECIMAL(5,2);


-- ============================================
-- 3. CREATE NEW TABLES (if not exists)
-- ============================================

-- Health Records (if not exists)
CREATE TABLE IF NOT EXISTS health_records (
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
-- NEW TABLE: MALNUTRITION CASES
-- ============================================
CREATE TABLE IF NOT EXISTS malnutrition_cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    record_id INT NOT NULL,
    malnutrition_type ENUM('underweight', 'stunting', 'wasting', 'overweight', 'obese', 'normal') NOT NULL,
    severity ENUM('none', 'mild', 'moderate', 'severe') DEFAULT 'none',
    bmi DECIMAL(5,2),
    weight_for_age_zscore DECIMAL(5,2),
    height_for_age_zscore DECIMAL(5,2),
    weight_for_height_zscore DECIMAL(5,2),
    muac DECIMAL(5,2),
    oedema BOOLEAN DEFAULT FALSE,
    status ENUM('active', 'recovered', 'referral_pending', 'closed') DEFAULT 'active',
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (record_id) REFERENCES health_records(id) ON DELETE CASCADE
);

-- ============================================
-- NEW TABLE: ALERTS
-- ============================================
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    alert_type ENUM('malnutrition_risk', 'follow_up_due', 'weight_loss', 'no_improvement', 'referral_required', 'appointment_reminder', 'system') NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    is_read BOOLEAN DEFAULT FALSE,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    assigned_to INT,
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================
-- NEW TABLE: MONITORING PLANS
-- ============================================
CREATE TABLE IF NOT EXISTS monitoring_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    created_by INT NOT NULL,
    plan_name VARCHAR(200),
    goal TEXT,
    target_weight DECIMAL(5,2),
    target_date DATE,
    status ENUM('active', 'completed', 'cancelled') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- NEW TABLE: FOLLOW-UPS
-- ============================================
CREATE TABLE IF NOT EXISTS follow_ups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    monitoring_plan_id INT,
    child_id INT NOT NULL,
    scheduled_date DATE NOT NULL,
    completed_date DATE,
    weight DECIMAL(5,2),
    height DECIMAL(5,2),
    muac DECIMAL(5,2),
    status VARCHAR(50),
    notes TEXT,
    next_follow_up_date DATE,
    conducted_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (monitoring_plan_id) REFERENCES monitoring_plans(id) ON DELETE SET NULL,
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (conducted_by) REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================
-- NEW TABLE: INTERVENTIONS
-- ============================================
CREATE TABLE IF NOT EXISTS interventions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    intervention_type ENUM('nutritional_counseling', 'supplementary_feeding', 'micronutrient_supplement', 'deworming', 'referral', 'other') NOT NULL,
    description TEXT,
    dosage VARCHAR(100),
    duration VARCHAR(100),
    status ENUM('prescribed', 'ongoing', 'completed', 'defaulted') DEFAULT 'prescribed',
    start_date DATE NOT NULL,
    end_date DATE,
    next_dose_date DATE,
    prescribed_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (prescribed_by) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- NEW TABLE: APPOINTMENTS
-- ============================================
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    appointment_date DATETIME NOT NULL,
    appointment_type ENUM('checkup', 'follow_up', 'vaccination', 'assessment', 'counseling', 'other') NOT NULL,
    location VARCHAR(200),
    notes TEXT,
    status ENUM('scheduled', 'completed', 'cancelled', 'no_show') DEFAULT 'scheduled',
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- NEW TABLE: WORKER ASSIGNMENTS
-- ============================================
CREATE TABLE IF NOT EXISTS worker_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nutrition_worker_id INT NOT NULL,
    child_id INT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (nutrition_worker_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_assignment (nutrition_worker_id, child_id)
);

-- ============================================
-- NEW TABLE: SYSTEM LOGS
-- ============================================
CREATE TABLE IF NOT EXISTS system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INT,
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================
-- ADD INDEXES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_children_parent ON children(parent_id);
CREATE INDEX IF NOT EXISTS idx_malnutrition_child ON malnutrition_cases(child_id);
CREATE INDEX IF NOT EXISTS idx_alerts_child ON alerts(child_id);
CREATE INDEX IF NOT EXISTS idx_alerts_priority ON alerts(priority);
CREATE INDEX IF NOT EXISTS idx_monitoring_child ON monitoring_plans(child_id);
CREATE INDEX IF NOT EXISTS idx_followups_child ON follow_ups(child_id);
CREATE INDEX IF NOT EXISTS idx_interventions_child ON interventions(child_id);
CREATE INDEX IF NOT EXISTS idx_appointments_child ON appointments(child_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_worker_assignments_worker ON worker_assignments(nutrition_worker_id);


