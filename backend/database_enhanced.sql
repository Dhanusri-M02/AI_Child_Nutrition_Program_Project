
-- ============================================
-- ENHANCED DATABASE SCHEMA FOR CHILD NUTRITION PROGRAM
-- Includes: Malnutrition Cases, Alerts, Monitoring
-- ============================================

-- Run this SQL in your MySQL database

-- ============================================
-- EXISTING TABLES (with enhancements)
-- ============================================

-- USERS TABLE (with role support)
CREATE TABLE IF NOT EXISTS users (
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

-- CHILDREN TABLE
CREATE TABLE IF NOT EXISTS children (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    sex ENUM('0', '1') NOT NULL,
    birth_weight DECIMAL(5,2),
    birth_height DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- NEW TABLE 1: MALNUTRITION CASES
-- ============================================
CREATE TABLE IF NOT EXISTS malnutrition_cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    record_id INT NOT NULL,
    
    -- Malnutrition Type
    malnutrition_type ENUM(
        'underweight',      -- Low weight for age
        'stunting',         -- Low height for age
        'wasting',          -- Low weight for height
        'overweight',       -- High weight for height
        'obese',            -- Severe overweight
        'normal'            -- For tracking recovery
    ) NOT NULL,
    
    -- Severity Level
    severity ENUM('none', 'mild', 'moderate', 'severe') DEFAULT 'none',
    
    -- BMI and Z-scores
    bmi DECIMAL(5,2),
    weight_for_age_zscore DECIMAL(5,2),
    height_for_age_zscore DECIMAL(5,2),
    weight_for_height_zscore DECIMAL(5,2),
    
    -- Additional assessments
    muac DECIMAL(5,2),  -- Mid-Upper Arm Circumference in cm
    oedema BOOLEAN DEFAULT FALSE,  -- Kwashiorkor indicator
    
    -- Status and dates
    status ENUM('active', 'recovered', 'referral_pending', 'closed') DEFAULT 'active',
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (record_id) REFERENCES health_records(id) ON DELETE CASCADE
);

-- ============================================
-- NEW TABLE 2: ALERTS & NOTIFICATIONS
-- ============================================
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    
    -- Alert Type
    alert_type ENUM(
        'malnutrition_risk',    -- High risk detected
        'follow_up_due',         -- Scheduled follow-up
        'weight_loss',          -- Concerning weight loss
        'no_improvement',       -- No progress over time
        'referral_required',    -- Needs medical attention
        'appointment_reminder', -- Upcoming appointment
        'system'                -- System-generated alert
    ) NOT NULL,
    
    -- Alert Details
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    is_resolved BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    
    -- Who it's assigned to
    assigned_to INT,  -- User ID (nutrition_worker or admin)
    
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================
-- NEW TABLE 3: MONITORING & FOLLOW-UP
-- ============================================
CREATE TABLE IF NOT EXISTS monitoring_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    created_by INT NOT NULL,
    
    -- Plan Details
    plan_name VARCHAR(200),
    goal TEXT,
    target_weight DECIMAL(5,2),
    target_date DATE,
    
    -- Status
    status ENUM('active', 'completed', 'cancelled') DEFAULT 'active',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS follow_ups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    monitoring_plan_id INT,
    child_id INT NOT NULL,
    
    -- Follow-up Details
    scheduled_date DATE NOT NULL,
    completed_date DATE,
    weight DECIMAL(5,2),
    height DECIMAL(5,2),
    muac DECIMAL(5,2),
    
    -- Assessment
    status VARCHAR(50),
    notes TEXT,
    next_follow_up_date DATE,
    
    -- Who conducted the follow-up
    conducted_by INT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (monitoring_plan_id) REFERENCES monitoring_plans(id) ON DELETE SET NULL,
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (conducted_by) REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================
-- NEW TABLE 4: INTERVENTIONS & TREATMENTS
-- ============================================
CREATE TABLE IF NOT EXISTS interventions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    
    -- Intervention Type
    intervention_type ENUM(
        'nutritional_counseling',   -- Dietary advice
        'supplementary_feeding',    -- Ready-to-use therapeutic food
        'micronutrient_supplement', -- Vitamin A, Iron, etc.
        'deworming',                -- Anti-parasitic treatment
        'referral',                  -- Referred to hospital/clinic
        'other'
    ) NOT NULL,
    
    -- Details
    description TEXT,
    dosage VARCHAR(100),
    duration VARCHAR(100),
    
    -- Status
    status ENUM('prescribed', 'ongoing', 'completed', 'defaulted') DEFAULT 'prescribed',
    
    -- Dates
    start_date DATE NOT NULL,
    end_date DATE,
    next_dose_date DATE,
    
    -- Prescribed by
    prescribed_by INT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (prescribed_by) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- NEW TABLE 5: APPOINTMENTS
-- ============================================
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    
    -- Appointment Details
    appointment_date DATETIME NOT NULL,
    appointment_type ENUM(
        'checkup',
        'follow_up',
        'vaccination',
        'assessment',
        'counseling',
        'other'
    ) NOT NULL,
    
    location VARCHAR(200),
    notes TEXT,
    
    -- Status
    status ENUM('scheduled', 'completed', 'cancelled', 'no_show') DEFAULT 'scheduled',
    
    -- Created by
    created_by INT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- NEW TABLE 6: NUTRITION WORKER ASSIGNMENTS
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
-- NEW TABLE 7: SYSTEM LOGS (for monitoring)
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
-- INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX idx_children_parent ON children(parent_id);
CREATE INDEX idx_malnutrition_child ON malnutrition_cases(child_id);
CREATE INDEX idx_malnutrition_type ON malnutrition_cases(malnutrition_type);
CREATE INDEX idx_alerts_child ON alerts(child_id);
CREATE INDEX idx_alerts_priority ON alerts(priority);
CREATE INDEX idx_alerts_read ON alerts(is_read);
CREATE INDEX idx_monitoring_child ON monitoring_plans(child_id);
CREATE INDEX idx_followups_child ON follow_ups(child_id);
CREATE INDEX idx_interventions_child ON interventions(child_id);
CREATE INDEX idx_appointments_child ON appointments(child_id);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_worker_assignments_worker ON worker_assignments(nutrition_worker_id);
CREATE INDEX idx_logs_user ON system_logs(user_id);
CREATE INDEX idx_logs_created ON system_logs(created_at);


