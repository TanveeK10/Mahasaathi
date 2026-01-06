-- MahaSaathi Database Schema
-- PostgreSQL database for Pune Ganeshotsav Assistant

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS rfid_activity CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS rfid_readers CASCADE;
DROP TABLE IF EXISTS locations CASCADE;

-- =====================================================
-- LOCATIONS TABLE
-- =====================================================
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('pandal','washroom','food','commutation','medical','security')),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL
);

-- Insert sample locations for testing
-- Pandals
INSERT INTO locations (name, category, latitude, longitude) VALUES
('Dagdusheth Halwai Ganpati Pandal', 'pandal', 18.5158, 73.8567),
('Kasba Ganpati Pandal', 'pandal', 18.5195, 73.8553),
('Tulshi Baug Ganpati Pandal', 'pandal', 18.5167, 73.8545),
('Kesariwada Ganpati Pandal', 'pandal', 18.5180, 73.8590),
('Tambdi Jogeshwari Ganpati Pandal', 'pandal', 18.5210, 73.8575);

-- Washrooms
INSERT INTO locations (name, category, latitude, longitude) VALUES
('Public Toilet - Laxmi Road', 'washroom', 18.5165, 73.8560),
('Public Toilet - Dagdusheth Area', 'washroom', 18.5160, 73.8570),
('Public Toilet - Kasba Area', 'washroom', 18.5200, 73.8550),
('Public Toilet - Tulshi Baug', 'washroom', 18.5170, 73.8548);

-- Food Stalls
INSERT INTO locations (name, category, latitude, longitude) VALUES
('Vaishali Restaurant', 'food', 18.5175, 73.8565),
('Roopali Restaurant', 'food', 18.5168, 73.8558),
('Goodluck Cafe', 'food', 18.5190, 73.8572),
('Street Food Stall - Laxmi Road', 'food', 18.5163, 73.8562);

-- Commutation (Metro/Bus Stations)
INSERT INTO locations (name, category, latitude, longitude) VALUES
('Mandai Metro Station', 'commutation', 18.5155, 73.8540),
('Budhwar Peth Bus Stop', 'commutation', 18.5172, 73.8555),
('Swargate Bus Stand', 'commutation', 18.5020, 73.8567),
('Pune Railway Station', 'commutation', 18.5284, 73.8742);

-- Medical Facilities
INSERT INTO locations (name, category, latitude, longitude) VALUES
('Sassoon General Hospital', 'medical', 18.5204, 73.8567),
('First Aid Center - Dagdusheth', 'medical', 18.5162, 73.8569),
('Ruby Hall Clinic', 'medical', 18.5314, 73.8446),
('Inamdar Hospital', 'medical', 18.5089, 73.8553);

-- Security Booths
INSERT INTO locations (name, category, latitude, longitude) VALUES
('Police Booth - Laxmi Road', 'security', 18.5166, 73.8563),
('Police Booth - Kasba Area', 'security', 18.5198, 73.8552),
('Police Booth - Tulshi Baug', 'security', 18.5169, 73.8547),
('Main Police Station - Faraskhana', 'security', 18.5185, 73.8580);

-- =====================================================
-- RFID READERS TABLE
-- =====================================================
CREATE TABLE rfid_readers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    zone INTEGER NOT NULL,
    x DOUBLE PRECISION,
    y DOUBLE PRECISION
);

-- Insert 6 RFID readers (2 per zone)
INSERT INTO rfid_readers (name, zone, x, y) VALUES
('Entry Gate A', 1, 18.5155, 73.8555),
('Entry Gate B', 1, 18.5157, 73.8558),
('Inner Temple Gate A', 2, 18.5160, 73.8565),
('Inner Temple Gate B', 2, 18.5162, 73.8568),
('Exit Gate A', 3, 18.5165, 73.8570),
('Exit Gate B', 3, 18.5167, 73.8572);

-- =====================================================
-- RFID ACTIVITY TABLE
-- =====================================================
CREATE TABLE rfid_activity (
    id SERIAL PRIMARY KEY,
    tag_uid TEXT NOT NULL,
    user_uid TEXT,
    reader_id INTEGER NOT NULL REFERENCES rfid_readers(id),
    zone INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Create index for faster queries
CREATE INDEX idx_rfid_activity_user_uid ON rfid_activity(user_uid);
CREATE INDEX idx_rfid_activity_zone_time ON rfid_activity(zone, created_at);
CREATE INDEX idx_rfid_activity_created_at ON rfid_activity(created_at);

-- =====================================================
-- USERS TABLE
-- =====================================================
CREATE TABLE users (
    user_uid TEXT PRIMARY KEY,
    last_seen_reader INTEGER REFERENCES rfid_readers(id),
    last_seen_zone INTEGER,
    last_seen_time TIMESTAMP
);

-- Insert sample test users
INSERT INTO users (user_uid, last_seen_reader, last_seen_zone, last_seen_time) VALUES
('test_user_001', 3, 2, now() - INTERVAL '2 minutes'),
('test_user_002', 5, 3, now() - INTERVAL '5 minutes'),
('test_user_003', 1, 1, now() - INTERVAL '10 minutes');

-- Insert sample RFID activity for testing crowd detection
INSERT INTO rfid_activity (tag_uid, user_uid, reader_id, zone, created_at) VALUES
('TAG001', 'test_user_001', 1, 1, now() - INTERVAL '10 minutes'),
('TAG001', 'test_user_001', 3, 2, now() - INTERVAL '2 minutes'),
('TAG002', 'test_user_002', 1, 1, now() - INTERVAL '8 minutes'),
('TAG002', 'test_user_002', 5, 3, now() - INTERVAL '5 minutes'),
('TAG003', 'test_user_003', 1, 1, now() - INTERVAL '10 minutes'),
('TAG004', NULL, 2, 1, now() - INTERVAL '4 minutes'),
('TAG005', NULL, 3, 2, now() - INTERVAL '3 minutes'),
('TAG006', NULL, 4, 2, now() - INTERVAL '2 minutes'),
('TAG007', NULL, 5, 3, now() - INTERVAL '1 minute'),
('TAG008', NULL, 1, 1, now() - INTERVAL '1 minute');

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Uncomment to verify data after setup:
-- SELECT category, COUNT(*) FROM locations GROUP BY category;
-- SELECT zone, COUNT(*) FROM rfid_readers GROUP BY zone;
-- SELECT COUNT(*) FROM users;
-- SELECT zone, COUNT(*) FROM rfid_activity WHERE created_at >= now() - INTERVAL '5 minutes' GROUP BY zone;
