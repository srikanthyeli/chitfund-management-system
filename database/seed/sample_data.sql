-- Seed script for testing local PostgreSQL database

-- Clear old records (in order of dependency)
TRUNCATE TABLE audit_logs CASCADE;
TRUNCATE TABLE passbook_entries CASCADE;
TRUNCATE TABLE collections CASCADE;
TRUNCATE TABLE bids CASCADE;
TRUNCATE TABLE auctions CASCADE;
TRUNCATE TABLE chit_memberships CASCADE;
TRUNCATE TABLE chit_groups CASCADE;
TRUNCATE TABLE members CASCADE;
TRUNCATE TABLE organizers CASCADE;
TRUNCATE TABLE users CASCADE;

-- 1. Insert Users (Auth Layer)
INSERT INTO users (id, mobile, password_hash, otp_enabled, role, is_active) VALUES
('11111111-1111-1111-1111-111111111111', '+919999999999', '$2b$12$K1r6tE1P0pA2o2U6iP0eOepR4Dbgw4k681hZ7vGv1nL1fR61w8p2C', false, 'ADMIN', true),
('22222222-2222-2222-2222-222222222222', '+918888888888', '$2b$12$K1r6tE1P0pA2o2U6iP0eOepR4Dbgw4k681hZ7vGv1nL1fR61w8p2C', false, 'ORGANIZER', true),
('33333333-3333-3333-3333-333333333333', '+917777777777', '$2b$12$K1r6tE1P0pA2o2U6iP0eOepR4Dbgw4k681hZ7vGv1nL1fR61w8p2C', true, 'MEMBER', true),
('44444444-4444-4444-4444-444444444444', '+916666666666', '$2b$12$K1r6tE1P0pA2o2U6iP0eOepR4Dbgw4k681hZ7vGv1nL1fR61w8p2C', true, 'MEMBER', true);

-- 2. Insert Organizers
INSERT INTO organizers (id, user_id, name, mobile) VALUES
('55555555-5555-5555-5555-555555555555', '22222222-2222-2222-2222-222222222222', 'Ramesh Kumar', '+918888888888');

-- 3. Insert Members
INSERT INTO members (id, user_id, name, mobile, address, status) VALUES
('66666666-6666-6666-6666-666666666666', '33333333-3333-3333-3333-333333333333', 'Suresh Rain', '+917777777777', '123, Gandhi Nagar, Bengaluru', 'ACTIVE'),
('77777777-7777-7777-7777-777777777777', '44444444-4444-4444-4444-444444444444', 'Mahesh Babu', '+916666666666', '456, Palace Road, Mysuru', 'ACTIVE');

-- 4. Insert Chit Groups
INSERT INTO chit_groups (id, organizer_id, name, duration_months, member_count, monthly_amount, maintenance_charge, start_date, status) VALUES
('88888888-8888-8888-8888-888888888888', '55555555-5555-5555-5555-555555555555', 'Kalyan ₹10k 50-Month', 50, 2, 10000.00, 25000.00, '2026-06-01', 'ACTIVE');

-- 5. Insert Chit Memberships (Ramesh and Suresh in GRP Kalyan)
INSERT INTO chit_memberships (id, chit_group_id, member_id, join_date, position_no, won_status) VALUES
('99999999-9999-9999-9999-999999999999', '88888888-8888-8888-8888-888888888888', '66666666-6666-6666-6666-666666666666', '2026-06-01 10:00:00', 1, false),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '88888888-8888-8888-8888-888888888888', '77777777-7777-7777-7777-777777777777', '2026-06-01 10:05:00', 2, false);
