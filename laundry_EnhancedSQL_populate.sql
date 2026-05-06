-- Clean up all tables (Order matters due to Foreign Keys)
DELETE FROM Wallet_Transaction;
DELETE FROM QR_Code;
DELETE FROM Laundry_Order;
DELETE FROM Cash_Wallet;
DELETE FROM Laundry_Machine;
DELETE FROM Pricing;
DELETE FROM Laundry_Staff;
DELETE FROM Student;

-- Reset sequences for SERIAL columns
ALTER SEQUENCE laundry_staff_staff_id_seq RESTART WITH 1;
ALTER SEQUENCE laundry_machine_machine_id_seq RESTART WITH 1;
ALTER SEQUENCE laundry_order_order_id_seq RESTART WITH 1;
ALTER SEQUENCE qr_code_qr_id_seq RESTART WITH 1;
ALTER SEQUENCE wallet_transaction_transaction_id_seq RESTART WITH 1;

-- 1. ADD STUDENTS (20 students across different dorms)
INSERT INTO Student (student_id, first_name, last_name, email, phone_number, residence, room, registered_at) VALUES
  (10001, 'Mohamed', 'Amghar', 'm.amghar@aui.ma', '0600000001', 'Dorm A', '101', '2025-09-01 10:00:00'),
  (10002, 'Saadia', 'Radi', 's.radi@aui.ma', '0600000002', 'Dorm B', '205', '2025-09-02 11:30:00'),
  (10003, 'Zouheir', 'Allali', 'z.allali@aui.ma', '0600000003', 'Dorm C', '302', '2025-09-05 09:15:00'),
  (10004, 'Sfia', 'Abijel', 's.abijel@aui.ma', '0600000004', 'Dorm A', '104', '2025-09-10 14:20:00'),
  (10005, 'Youssef', 'Benali', 'y.benali@aui.ma', '0600000005', 'Dorm A', '102', '2025-09-03 08:45:00'),
  (10006, 'Fatima', 'Zahra', 'f.zahra@aui.ma', '0600000006', 'Dorm B', '201', '2025-09-07 16:30:00'),
  (10007, 'Omar', 'El Amrani', 'o.elamrani@aui.ma', '0600000007', 'Dorm C', '305', '2025-09-12 13:00:00'),
  (10008, 'Amina', 'Tazi', 'a.tazi@aui.ma', '0600000008', 'Dorm A', '203', '2025-09-15 10:30:00'),
  (10009, 'Hassan', 'Idrissi', 'h.idrissi@aui.ma', '0600000009', 'Dorm B', '304', '2025-09-18 09:00:00'),
  (10010, 'Salma', 'Benjelloun', 's.benjelloun@aui.ma', '0600000010', 'Dorm C', '401', '2025-09-20 15:45:00'),
  (10011, 'Rachid', 'Ouazzani', 'r.ouazzani@aui.ma', '0600000011', 'Dorm A', '105', '2025-10-01 11:00:00'),
  (10012, 'Nadia', 'Cherkaoui', 'n.cherkaoui@aui.ma', '0600000012', 'Dorm B', '206', '2025-10-05 08:30:00'),
  (10013, 'Karim', 'El Fassi', 'k.elfassi@aui.ma', '0600000013', 'Dorm C', '303', '2025-10-10 14:15:00'),
  (10014, 'Leila', 'Alaoui', 'l.alaoui@aui.ma', '0600000014', 'Dorm A', '106', '2025-10-15 10:00:00'),
  (10015, 'Mehdi', 'Bennouna', 'm.bennouna@aui.ma', '0600000015', 'Dorm B', '207', '2025-10-20 16:45:00'),
  (10016, 'Soukaina', 'Doukkali', 's.doukkali@aui.ma', '0600000016', 'Dorm C', '402', '2025-10-25 09:30:00'),
  (10017, 'Anas', 'Boutaleb', 'a.boutaleb@aui.ma', '0600000017', 'Dorm A', '107', '2025-11-01 13:00:00'),
  (10018, 'Meryem', 'Kabbaj', 'm.kabbaj@aui.ma', '0600000018', 'Dorm B', '208', '2025-11-05 11:15:00'),
  (10019, 'Adil', 'Lahlou', 'a.lahlou@aui.ma', '0600000019', 'Dorm C', '403', '2025-11-10 08:00:00'),
  (10020, 'Hanane', 'Berrada', 'h.berrada@aui.ma', '0600000020', 'Dorm A', '108', '2025-11-15 15:30:00'),
  (10021, 'Tarik', 'Sebbani', 't.sebbani@aui.ma', '0600000021', 'Dorm B', '301', '2025-12-01 10:00:00'),
  (10022, 'Imane', 'Rahmani', 'i.rahmani@aui.ma', '0600000022', 'Dorm C', '404', '2025-12-05 14:30:00'),
  (10023, 'Bilal', 'Chraibi', 'b.chraibi@aui.ma', '0600000023', 'Dorm A', '109', '2025-12-10 09:45:00'),
  (10024, 'Samira', 'El Khattabi', 's.elkhattabi@aui.ma', '0600000024', 'Dorm B', '302', '2025-12-15 16:00:00'),
  (10025, 'Driss', 'Bencheikh', 'd.bencheikh@aui.ma', '0600000025', 'Dorm C', '405', '2026-01-05 11:30:00');

-- 2. ADD CASH WALLETS (linked by student_id, with varied balances)
INSERT INTO Cash_Wallet (student_id, balance) VALUES
  (10001, 120.00),
  (10002, 75.50),
  (10003, 30.00),
  (10004, 0.00),
  (10005, 200.00),
  (10006, 45.75),
  (10007, 15.00),
  (10008, 85.25),
  (10009, 50.00),
  (10010, 100.00),
  (10011, 0.00),
  (10012, 67.80),
  (10013, 150.00),
  (10014, 33.50),
  (10015, 90.00),
  (10016, 25.00),
  (10017, 180.00),
  (10018, 42.00),
  (10019, 0.00),
  (10020, 55.50),
  (10021, 110.00),
  (10022, 70.25),
  (10023, 0.00),
  (10024, 95.00),
  (10025, 40.00);

-- 3. ADD LAUNDRY STAFF (10 staff members with different roles)
INSERT INTO Laundry_Staff (first_name, last_name, role, email) VALUES
  ('Karim', 'Haddad', 'Manager', 'k.haddad@aui.ma'),
  ('Lamiae', 'Bennani', 'Operator', 'l.bennani@aui.ma'),
  ('Hicham', 'Safi', 'Technician', 'h.safi@aui.ma'),
  ('Nawal', 'El Idrissi', 'Supervisor', 'n.elidrissi@aui.ma'),
  ('Abdelali', 'Mouline', 'Operator', 'a.mouline@aui.ma'),
  ('Sanae', 'Kettani', 'Technician', 's.kettani@aui.ma'),
  ('Rachid', 'Bennis', 'Operator', 'r.bennis@aui.ma'),
  ('Fatiha', 'Lahbabi', 'Operator', 'f.lahbabi@aui.ma'),
  ('Mustapha', 'Senhaji', 'Technician', 'm.senhaji@aui.ma'),
  ('Meriem', 'Ouahbi', 'Customer Service', 'm.ouahbi@aui.ma');

-- 4. ADD PRICING (more service types)
INSERT INTO Pricing (service_type, price_per_kg) VALUES
  ('Wash', 5.00),
  ('Dry', 4.00),
  ('Wash & Dry', 8.50),
  ('Ironing', 6.00),
  ('Dry Cleaning', 12.00),
  ('Express Wash', 7.50),
  ('Express Wash & Dry', 12.00),
  ('Delicates', 15.00),
  ('Comforter/Blanket', 20.00),
  ('Stain Removal', 10.00),
  ('Detergent Pod', 10.00);

-- 5. ADD LAUNDRY MACHINES (12 machines across multiple rooms)
INSERT INTO Laundry_Machine (machine_type, brand_model, capacity_kg, current_status, location) VALUES
  ('Washer', 'LG TurboWash 3000', 10.0, 'Available', 'Room 1'),
  ('Dryer', 'Samsung DryPro X', 8.0, 'Available', 'Room 1'),
  ('Washer', 'Bosch EcoWash', 12.0, 'Maintenance', 'Room 2'),
  ('Washer', 'LG TurboWash 4000', 14.0, 'Available', 'Room 2'),
  ('Dryer', 'Samsung DryPro Y', 10.0, 'In Use', 'Room 2'),
  ('Washer', 'Whirlpool PowerWash', 11.0, 'Available', 'Room 3'),
  ('Dryer', 'LG DrySense', 9.0, 'Available', 'Room 3'),
  ('Washer', 'Electrolux ProClean', 15.0, 'Available', 'Room 3'),
  ('Dryer', 'Electrolux DryTech', 12.0, 'In Use', 'Room 3'),
  ('Washer', 'Haier DoubleDrum', 8.0, 'Available', 'Room 1'),
  ('Dryer', 'Bosch DryElite', 7.0, 'Maintenance', 'Room 1'),
  ('Washer', 'Miele Professional', 16.0, 'Available', 'Room 2');

-- 6. ADD LAUNDRY ORDERS (30 orders with various statuses, dates, and services)
INSERT INTO Laundry_Order (student_id, staff_id, machine_id, service_type, weight_kg, total_price, order_status, dropoff_date, expected_pickup, actual_pickup, payment_status, notes) VALUES
  -- Completed orders
  (10001, 2, 1, 'Wash & Dry', 3.0, 25.50, 'Completed', '2026-03-01 09:00:00', '2026-03-03 12:00:00', '2026-03-03 14:00:00', 'Paid', 'Urgent order'),
  (10005, 5, 4, 'Express Wash & Dry', 2.0, 24.00, 'Completed', '2026-03-01 10:00:00', '2026-03-01 16:00:00', '2026-03-01 15:30:00', 'Paid', NULL),
  (10006, 2, 1, 'Wash', 4.0, 20.00, 'Completed', '2026-03-02 08:00:00', '2026-03-04 08:00:00', '2026-03-04 09:00:00', 'Paid', 'Sports clothes'),
  (10008, 5, 6, 'Dry Cleaning', 2.5, 30.00, 'Completed', '2026-03-02 14:00:00', '2026-03-04 14:00:00', '2026-03-04 13:45:00', 'Paid', 'Formal suit'),
  (10010, 7, 8, 'Wash', 6.0, 30.00, 'Completed', '2026-03-03 11:00:00', '2026-03-05 11:00:00', '2026-03-05 10:30:00', 'Paid', NULL),
  (10013, 2, 1, 'Wash & Dry', 3.5, 29.75, 'Completed', '2026-03-03 13:00:00', '2026-03-05 13:00:00', '2026-03-05 14:00:00', 'Paid', 'Weekly laundry'),
  (10015, 4, 10, 'Ironing', 5.0, 30.00, 'Completed', '2026-03-04 09:00:00', '2026-03-05 09:00:00', '2026-03-05 08:45:00', 'Paid', 'Shirts and pants'),
  (10017, 8, 12, 'Express Wash', 1.5, 11.25, 'Completed', '2026-03-04 15:00:00', '2026-03-04 21:00:00', '2026-03-04 20:30:00', 'Paid', NULL),
  
  -- In Progress orders
  (10002, 2, 2, 'Dry', 4.0, 16.00, 'In Progress', '2026-03-10 10:00:00', '2026-03-12 10:00:00', NULL, 'Paid', 'Blankets'),
  (10007, 5, 5, 'Wash & Dry', 3.0, 25.50, 'In Progress', '2026-03-10 11:00:00', '2026-03-12 11:00:00', NULL, 'Paid', NULL),
  (10012, 7, 9, 'Dry', 2.5, 10.00, 'In Progress', '2026-03-10 14:00:00', '2026-03-13 14:00:00', NULL, 'Pending', 'Towels'),
  (10014, 2, 1, 'Wash', 5.5, 27.50, 'In Progress', '2026-03-11 09:00:00', '2026-03-13 09:00:00', NULL, 'Paid', NULL),
  (10018, 8, 10, 'Delicates', 1.0, 15.00, 'In Progress', '2026-03-11 10:00:00', '2026-03-13 10:00:00', NULL, 'Pending', 'Silk dresses'),
  (10020, 5, 4, 'Wash & Dry', 4.0, 34.00, 'In Progress', '2026-03-11 15:00:00', '2026-03-13 15:00:00', NULL, 'Paid', NULL),
  
  -- Pending orders
  (10003, 4, 3, 'Wash', 5.0, 25.00, 'Pending', '2026-03-15 14:00:00', '2026-03-18 14:00:00', NULL, 'Unpaid', 'Large blanket'),
  (10009, 2, 1, 'Express Wash & Dry', 2.5, 30.00, 'Pending', '2026-03-15 15:00:00', '2026-03-15 21:00:00', NULL, 'Unpaid', 'Urgent'),
  (10021, 7, 6, 'Wash', 3.0, 15.00, 'Pending', '2026-03-15 16:00:00', '2026-03-18 16:00:00', NULL, 'Unpaid', NULL),
  (10022, 5, 8, 'Ironing', 4.5, 27.00, 'Pending', '2026-03-16 09:00:00', '2026-03-17 09:00:00', NULL, 'Unpaid', 'Business attire'),
  (10024, 8, 12, 'Stain Removal', 2.0, 20.00, 'Pending', '2026-03-16 10:00:00', '2026-03-18 10:00:00', NULL, 'Unpaid', 'Coffee stain'),
  (10025, 2, 1, 'Wash & Dry', 3.5, 29.75, 'Pending', '2026-03-16 11:00:00', '2026-03-18 11:00:00', NULL, 'Unpaid', NULL),
  
  -- Cancelled orders
  (10004, 4, 3, 'Express Wash', 1.0, 7.50, 'Cancelled', '2026-03-05 08:00:00', '2026-03-05 14:00:00', NULL, 'Refunded', 'Changed mind'),
  (10011, 5, 6, 'Wash', 3.0, 15.00, 'Cancelled', '2026-03-06 10:00:00', '2026-03-08 10:00:00', NULL, 'Refunded', 'Machine breakdown'),
  (10016, 7, 5, 'Dry', 2.0, 8.00, 'Cancelled', '2026-03-07 12:00:00', '2026-03-09 12:00:00', NULL, 'Refunded', NULL),
  
  -- Completed with different dates (March 8-14)
  (10001, 2, 1, 'Wash & Dry', 3.0, 25.50, 'Completed', '2026-03-08 09:00:00', '2026-03-10 12:00:00', '2026-03-10 14:00:00', 'Paid', 'Regular wash'),
  (10005, 5, 4, 'Comforter/Blanket', 6.0, 120.00, 'Completed', '2026-03-08 10:00:00', '2026-03-10 10:00:00', '2026-03-10 09:30:00', 'Paid', 'Winter comforter'),
  (10008, 7, 8, 'Dry Cleaning', 3.0, 36.00, 'Completed', '2026-03-09 11:00:00', '2026-03-11 11:00:00', '2026-03-11 10:45:00', 'Paid', 'Evening gown'),
  (10013, 2, 1, 'Wash', 5.5, 27.50, 'Completed', '2026-03-09 14:00:00', '2026-03-11 14:00:00', '2026-03-11 13:30:00', 'Paid', NULL),
  (10020, 5, 4, 'Express Wash & Dry', 1.5, 18.00, 'Completed', '2026-03-10 08:00:00', '2026-03-10 14:00:00', '2026-03-10 13:45:00', 'Paid', 'Last minute'),
  (10024, 8, 10, 'Delicates', 0.8, 12.00, 'Completed', '2026-03-10 13:00:00', '2026-03-12 13:00:00', '2026-03-12 12:30:00', 'Paid', 'Lingerie');

-- 7. ADD QR CODES (matching all orders above)
INSERT INTO QR_Code (order_id, qr_code_string) VALUES
  (1, 'QR_501_STUDENT1001'),
  (2, 'QR_502_STUDENT1005'),
  (3, 'QR_503_STUDENT1006'),
  (4, 'QR_504_STUDENT1008'),
  (5, 'QR_505_STUDENT1010'),
  (6, 'QR_506_STUDENT1013'),
  (7, 'QR_507_STUDENT1015'),
  (8, 'QR_508_STUDENT1017'),
  (9, 'QR_509_STUDENT1002'),
  (10, 'QR_510_STUDENT1007'),
  (11, 'QR_511_STUDENT1012'),
  (12, 'QR_512_STUDENT1014'),
  (13, 'QR_513_STUDENT1018'),
  (14, 'QR_514_STUDENT1020'),
  (15, 'QR_515_STUDENT1003'),
  (16, 'QR_516_STUDENT1009'),
  (17, 'QR_517_STUDENT1021'),
  (18, 'QR_518_STUDENT1022'),
  (19, 'QR_519_STUDENT1024'),
  (20, 'QR_520_STUDENT1025'),
  (21, 'QR_521_STUDENT1004'),
  (22, 'QR_522_STUDENT1011'),
  (23, 'QR_523_STUDENT1016'),
  (24, 'QR_524_STUDENT1001_BATCH2'),
  (25, 'QR_525_STUDENT1005_BATCH2'),
  (26, 'QR_526_STUDENT1008_BATCH2'),
  (27, 'QR_527_STUDENT1013_BATCH2'),
  (28, 'QR_528_STUDENT1020_BATCH2'),
  (29, 'QR_529_STUDENT1024_BATCH2');

-- 8. ADD WALLET TRANSACTIONS (lots of transactions for financial history)
INSERT INTO Wallet_Transaction (student_id, order_id, amount, transaction_type) VALUES
  -- Initial deposits
  (10001, NULL, 150.00, 'Deposit'),
  (10002, NULL, 100.00, 'Deposit'),
  (10003, NULL, 50.00, 'Deposit'),
  (10004, NULL, 30.00, 'Deposit'),
  (10005, NULL, 200.00, 'Deposit'),
  (10006, NULL, 80.00, 'Deposit'),
  (10007, NULL, 40.00, 'Deposit'),
  (10008, NULL, 120.00, 'Deposit'),
  (10009, NULL, 60.00, 'Deposit'),
  (10010, NULL, 150.00, 'Deposit'),
  (10011, NULL, 20.00, 'Deposit'),
  (10012, NULL, 90.00, 'Deposit'),
  (10013, NULL, 200.00, 'Deposit'),
  (10014, NULL, 60.00, 'Deposit'),
  (10015, NULL, 120.00, 'Deposit'),
  (10016, NULL, 50.00, 'Deposit'),
  (10017, NULL, 200.00, 'Deposit'),
  (10018, NULL, 70.00, 'Deposit'),
  (10019, NULL, 30.00, 'Deposit'),
  (10020, NULL, 100.00, 'Deposit'),
  (10021, NULL, 150.00, 'Deposit'),
  (10022, NULL, 100.00, 'Deposit'),
  (10023, NULL, 25.00, 'Deposit'),
  (10024, NULL, 130.00, 'Deposit'),
  (10025, NULL, 80.00, 'Deposit'),
  
  -- Top-up deposits
  (10001, NULL, 50.00, 'Deposit'),
  (10003, NULL, 30.00, 'Deposit'),
  (10006, NULL, 40.00, 'Deposit'),
  (10008, NULL, 60.00, 'Deposit'),
  (10012, NULL, 30.00, 'Deposit'),
  (10015, NULL, 50.00, 'Deposit'),
  (10020, NULL, 75.00, 'Deposit'),
  (10022, NULL, 45.00, 'Deposit'),
  (10025, NULL, 25.00, 'Deposit'),
  
  -- Laundry payments (first batch of orders)
  (10001, 1, -25.50, 'Laundry Payment'),
  (10005, 2, -24.00, 'Laundry Payment'),
  (10006, 3, -20.00, 'Laundry Payment'),
  (10008, 4, -30.00, 'Laundry Payment'),
  (10010, 5, -30.00, 'Laundry Payment'),
  (10013, 6, -29.75, 'Laundry Payment'),
  (10015, 7, -30.00, 'Laundry Payment'),
  (10017, 8, -11.25, 'Laundry Payment'),
  
  -- Laundry payments (in-progress orders)
  (10002, 9, -16.00, 'Laundry Payment'),
  (10007, 10, -25.50, 'Laundry Payment'),
  (10014, 12, -27.50, 'Laundry Payment'),
  (10020, 14, -34.00, 'Laundry Payment'),
  
  -- Refunds for cancelled orders
  (10004, NULL, 7.50, 'Refund'),
  (10011, NULL, 15.00, 'Refund'),
  (10016, NULL, 8.00, 'Refund'),
  
  -- Laundry payments (second batch)
  (10001, 24, -25.50, 'Laundry Payment'),
  (10005, 25, -120.00, 'Laundry Payment'),
  (10008, 26, -36.00, 'Laundry Payment'),
  (10013, 27, -27.50, 'Laundry Payment'),
  (10020, 28, -18.00, 'Laundry Payment'),
  (10024, 29, -12.00, 'Laundry Payment'),
  
  -- Additional top-ups for heavy users
  (10005, NULL, 100.00, 'Deposit'),
  (10008, NULL, 50.00, 'Deposit'),
  (10013, NULL, 75.00, 'Deposit'),
  (10020, NULL, 40.00, 'Deposit'),
  
  -- Miscellaneous transactions
  (10001, NULL, 10.00, 'Bonus'),
  (10005, NULL, 15.00, 'Referral Bonus'),
  (10010, NULL, 5.00, 'Loyalty Credit'),
  (10015, NULL, 10.00, 'Bonus'),
  (10020, NULL, 8.00, 'Promotional Credit'),
  
  -- Potential future payments (for pending orders)
  (10003, NULL, -25.00, 'Payment Hold'),
  (10009, NULL, -30.00, 'Payment Hold'),
  (10021, NULL, -15.00, 'Payment Hold'),
  (10022, NULL, -27.00, 'Payment Hold'),
  (10024, NULL, -20.00, 'Payment Hold'),
  (10025, NULL, -29.75, 'Payment Hold');