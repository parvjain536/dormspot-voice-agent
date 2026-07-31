-- DormSpot Database Schema for Supabase PostgreSQL
-- Run this script inside the Supabase SQL Editor

-- 1. Create Hostels Table
CREATE TABLE IF NOT EXISTS hostels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    room_type VARCHAR(50) NOT NULL DEFAULT 'Sharing',
    price_per_night NUMERIC(10, 2) NOT NULL,
    rooms_available INT NOT NULL DEFAULT 0,
    amenities TEXT[] DEFAULT '{}',
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create Bookings Table
CREATE TABLE IF NOT EXISTS bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hostel_id UUID REFERENCES hostels(id) ON DELETE CASCADE,
    guest_name VARCHAR(255) NOT NULL,
    guest_phone VARCHAR(20) NOT NULL,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'confirmed',
    booking_code VARCHAR(20) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Seed Realistic Dummy Data (Bhopal, Indore, Pune, Gwalior)
INSERT INTO hostels (name, city, room_type, price_per_night, rooms_available, amenities, address) VALUES
('DormSpot Scholar Hub', 'Bhopal', 'Single AC', 650.00, 4, ARRAY['Free WiFi', '3-Time Meals', 'Biometric Security', 'Study Room'], 'MP Nagar Zone 2, Bhopal'),
('DormSpot GreenView PG', 'Bhopal', 'Double Sharing', 450.00, 0, ARRAY['Free WiFi', 'Laundry', 'CCTV'], 'Indrapuri Sector C, Bhopal'),
('DormSpot TechHaven Co-Living', 'Indore', 'Single AC Studio', 850.00, 6, ARRAY['High-Speed WiFi', 'Gym', 'Meals Included', 'Power Backup'], 'Vijay Nagar, Indore'),
('DormSpot Campus Edge', 'Indore', 'Triple Sharing', 390.00, 2, ARRAY['Free WiFi', 'Housekeeping', 'RO Water'], 'Bhawarkua, Indore'),
('DormSpot Metro Residency', 'Pune', 'Single AC Premium', 950.00, 5, ARRAY['WiFi', 'Gaming Zone', 'Daily Housekeeping', 'AC'], 'Hinjewadi Phase 1, Pune'),
('DormSpot Heritage Student Stay', 'Gwalior', 'Double Non-AC', 400.00, 3, ARRAY['Free WiFi', 'Home Style Meals', '24/7 Security'], 'City Center, Gwalior');
