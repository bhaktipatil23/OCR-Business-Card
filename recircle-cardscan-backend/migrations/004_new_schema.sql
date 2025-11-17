-- Create new database
CREATE DATABASE IF NOT EXISTS business_card_ocr;
USE business_card_ocr;

-- Create events table (stores form data from popup)
CREATE TABLE events (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL COMMENT 'User name from popup',
    team VARCHAR(255) NOT NULL COMMENT 'Team name from popup', 
    batch_id VARCHAR(255) UNIQUE NOT NULL COMMENT 'Batch ID as foreign key',
    event VARCHAR(255) NOT NULL COMMENT 'Event name from popup',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create business_cards table (stores extracted OCR data)
CREATE TABLE business_cards (
    id INT PRIMARY KEY AUTO_INCREMENT,
    batch_id VARCHAR(255) NOT NULL COMMENT 'Batch ID as primary key reference',
    name VARCHAR(255) COMMENT 'Extracted person name',
    phone VARCHAR(50) COMMENT 'Extracted phone number',
    email VARCHAR(255) COMMENT 'Extracted email address',
    company VARCHAR(255) COMMENT 'Extracted company name',
    designation VARCHAR(255) COMMENT 'Extracted job title',
    address TEXT COMMENT 'Extracted address',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES events(batch_id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_events_batch_id ON events(batch_id);
CREATE INDEX idx_business_cards_batch_id ON business_cards(batch_id);