-- Create events table (stores form data from popup)
CREATE TABLE events (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    team VARCHAR(255) NOT NULL, 
    batch_id VARCHAR(255) UNIQUE NOT NULL,
    event VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create business_cards table (stores extracted OCR data)
CREATE TABLE business_cards (
    id INT PRIMARY KEY AUTO_INCREMENT,
    batch_id VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),
    company VARCHAR(255),
    designation VARCHAR(255),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES events(batch_id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX idx_events_batch_id ON events(batch_id);
CREATE INDEX idx_business_cards_batch_id ON business_cards(batch_id);