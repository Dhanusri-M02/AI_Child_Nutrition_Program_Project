
-- Quick fix for children table - adds missing columns and makes date_of_birth optional
-- Run this in phpMyAdmin to fix the error without losing data

-- First, make date_of_birth allow NULL (optional)
ALTER TABLE children MODIFY COLUMN date_of_birth DATE NULL;

-- Add the missing columns
ALTER TABLE children ADD COLUMN age DECIMAL(5,2) NOT NULL;
ALTER TABLE children ADD COLUMN weight DECIMAL(5,2) NOT NULL;
ALTER TABLE children ADD COLUMN height DECIMAL(5,2) NOT NULL;

