-- Step 1: Run this first
CREATE TABLE events (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    team VARCHAR(255) NOT NULL, 
    batch_id VARCHAR(255) UNIQUE NOT NULL,
    event VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 2: Run this second  
CREATE TABLE business_cards (
    id INT PRIMARY KEY AUTO_INCREMENT,
    batch_id VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),
    company VARCHAR(255),
    designation VARCHAR(255),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 3: Run this third (after both tables exist)
ALTER TABLE business_cards 
ADD CONSTRAINT fk_batch_id 
FOREIGN KEY (batch_id) REFERENCES events(batch_id) ON DELETE CASCADE;

-- Step 4: Run these last
CREATE INDEX idx_events_batch_id ON events(batch_id);
CREATE INDEX idx_business_cards_batch_id ON business_cards(batch_id);