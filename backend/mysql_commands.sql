-- ============================================
-- RUN THESE COMMANDS IN MYSQL (phpMyAdmin)
-- ============================================

-- ============================================
-- PART 1: ALTER EXISTING TABLES
-- ============================================

-- Add role column to users table
ALTER TABLE users ADD COLUMN role ENUM('parent', 'nutrition_worker', 'admin') NOT NULL DEFAULT 'parent';

-- Add phone column to users table
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Add date_of_birth to children table
ALTER TABLE children ADD COLUMN date_of_birth DATE;

-- Add birth_weight to children table
ALTER TABLE children ADD COLUMN birth_weight DECIMAL(5,2);

-- Add birth_height to children table
ALTER TABLE children ADD COLUMN birth_height DECIMAL(5,2);



-- ============================================
-- PART 2: CREATE NEW TABLES
-- ============================================

-- Create health_records table
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

-- Create malnutrition_cases table
CREATE TABLE malnutrition_cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    record_id INT NOT NULL,
    malnutrition_type ENUM('underweight', 'stunting', 'wasting', 'overweight', 'obese', 'normal') NOT NULL,
    severity ENUM('none', 'mild', 'moderate', 'severe') DEFAULT 'none',
    bmi DECIMAL(5,2),
    status ENUM('active', 'recovered', 'referral_pending', 'closed') DEFAULT 'active',
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (record_id) REFERENCES health_records(id) ON DELETE CASCADE
);

-- Create alerts table
CREATE TABLE alerts (
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

-- Create monitoring_plans table
CREATE TABLE monitoring_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    created_by INT NOT NULL,
    plan_name VARCHAR(200),
    goal TEXT,
    target_weight DECIMAL(5,2),
    target_date DATE,
    status ENUM('active', 'completed', 'cancelled') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

-- Create follow_ups table
CREATE TABLE follow_ups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    monitoring_plan_id INT,
    child_id INT NOT NULL,
    scheduled_date DATE NOT NULL,
    completed_date DATE,
    weight DECIMAL(5,2),
    height DECIMAL(5,2),
    notes TEXT,
    conducted_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (monitoring_plan_id) REFERENCES monitoring_plans(id) ON DELETE SET NULL,
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (conducted_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Create interventions table
CREATE TABLE interventions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    intervention_type ENUM('nutritional_counseling', 'supplementary_feeding', 'micronutrient_supplement', 'deworming', 'referral', 'other') NOT NULL,
    description TEXT,
    status ENUM('prescribed', 'ongoing', 'completed', 'defaulted') DEFAULT 'prescribed',
    start_date DATE NOT NULL,
    end_date DATE,
    prescribed_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (prescribed_by) REFERENCES users(id) ON DELETE CASCADE
);

-- Create appointments table
CREATE TABLE appointments (
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

-- Create worker_assignments table
CREATE TABLE worker_assignments (
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

-- Create system_logs table
CREATE TABLE system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INT,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);
