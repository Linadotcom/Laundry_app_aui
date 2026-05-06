-- 0. CLEANUP (Run this to start fresh)
DROP TABLE IF EXISTS Wallet_Transaction CASCADE;
DROP TABLE IF EXISTS QR_Code CASCADE;
DROP TABLE IF EXISTS Laundry_Order CASCADE;
DROP TABLE IF EXISTS Laundry_Machine CASCADE;
DROP TABLE IF EXISTS Pricing CASCADE;
DROP TABLE IF EXISTS Laundry_Staff CASCADE;
DROP TABLE IF EXISTS Cash_Wallet CASCADE;
DROP TABLE IF EXISTS Student CASCADE;

-- 1. STUDENT
CREATE TABLE Student (
    student_id INT PRIMARY KEY, 
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    residence VARCHAR(100),
    room VARCHAR(100),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. CASH WALLET
CREATE TABLE Cash_Wallet (
    student_id INT PRIMARY KEY,
    balance DECIMAL(10,2) DEFAULT 0.00,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE
);

-- 3. LAUNDRY STAFF
CREATE TABLE Laundry_Staff (
    staff_id SERIAL PRIMARY KEY, -- SERIAL is Postgres's AUTO_INCREMENT
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role VARCHAR(50),
    email VARCHAR(100) UNIQUE
);

-- 4. PRICINGELECT 
    p.service_type,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_price) AS total_revenue,
    AVG(o.total_price) AS average_order_value
FROM Pricing p
LEFT JOIN Laundry_Order o ON p.service_type = o.service_type
GROUP BY p.service_type;
CREATE TABLE Pricing (
    service_type VARCHAR(50) PRIMARY KEY,
    price_per_kg DECIMAL(10,2) NOT NULL
);

-- 5. LAUNDRY MACHINE
CREATE TABLE Laundry_Machine (
    machine_id SERIAL PRIMARY KEY,
    machine_type VARCHAR(50), 
    brand_model VARCHAR(100),
    capacity_kg DECIMAL(5,2),
    current_status VARCHAR(50) DEFAULT 'Available',
    location VARCHAR(100)
);

-- 6. LAUNDRY ORDER
CREATE TABLE Laundry_Order (
    order_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    staff_id INT,
    machine_id INT,
    service_type VARCHAR(50), 
    weight_kg DECIMAL(5,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL, 
    order_status VARCHAR(50) DEFAULT 'Pending',
    dropoff_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expected_pickup TIMESTAMP, -- Changed from DATETIME to TIMESTAMP
    actual_pickup TIMESTAMP,   -- Changed from DATETIME to TIMESTAMP
    payment_status VARCHAR(50) DEFAULT 'Unpaid',
    notes TEXT,
    
    FOREIGN KEY (student_id) REFERENCES Student(student_id),
    FOREIGN KEY (staff_id) REFERENCES Laundry_Staff(staff_id),
    FOREIGN KEY (machine_id) REFERENCES Laundry_Machine(machine_id),
    FOREIGN KEY (service_type) REFERENCES Pricing(service_type)
);

-- 7. QR CODE
CREATE TABLE QR_Code (
    qr_id SERIAL PRIMARY KEY,
    order_id INT UNIQUE NOT NULL,
    qr_code_string VARCHAR(255) UNIQUE NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES Laundry_Order(order_id) ON DELETE CASCADE
);

-- 8. WALLET TRANSACTIONS
CREATE TABLE Wallet_Transaction (
    transaction_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    order_id INT, 
    amount DECIMAL(10,2) NOT NULL, 
    transaction_type VARCHAR(50),  
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES Student(student_id),
    FOREIGN KEY (order_id) REFERENCES Laundry_Order(order_id)
);


-- ==========================================
-- LAYER 1: DATABASE VIEWS
-- ==========================================

-- View 1: Manager_Dashboard
CREATE OR REPLACE VIEW Manager_Dashboard AS
SELECT 
    lo.order_id,
    s.first_name || ' ' || s.last_name AS student_name,
    lm.brand_model AS machine_name,
    lo.service_type,
    lo.order_status,
    lo.total_price
FROM Laundry_Order lo
JOIN Student s ON lo.student_id = s.student_id
JOIN Laundry_Machine lm ON lo.machine_id = lm.machine_id;

-- View 2: Machine_Health_Report
CREATE OR REPLACE VIEW Machine_Health_Report AS
SELECT 
    machine_id,
    brand_model,
    usage_count,
    CASE 
        WHEN usage_count > 10 THEN 'Maintenance Needed'
        WHEN usage_count > 5 THEN 'Check Soon'
        ELSE 'Good Condition'
    END AS maintenance_status
FROM Laundry_Machine;

-- View 3: Student_Spending_Summary
CREATE OR REPLACE VIEW Student_Spending_Summary AS
SELECT 
    s.first_name || ' ' || s.last_name AS student_name,
    COUNT(lo.order_id) AS total_orders,
    SUM(lo.total_price) AS total_money_spent
FROM Laundry_Order lo
JOIN Student s ON lo.student_id = s.student_id
GROUP BY s.first_name, s.last_name;

-- ==========================================
-- LAYER 2: DATABASE FUNCTIONS
-- ==========================================

-- Function 1: get_total_spent
CREATE OR REPLACE FUNCTION get_total_spent(target_student_id INT)
RETURNS DECIMAL(10,2) AS $$
DECLARE 
    total DECIMAL(10,2);
BEGIN
    SELECT COALESCE(SUM(total_price), 0.00) INTO total
    FROM Laundry_Order
    WHERE student_id = target_student_id AND order_status = 'Completed';
    
    RETURN total;
END;
$$ LANGUAGE plpgsql;

-- Function 2: is_machine_available
CREATE OR REPLACE FUNCTION is_machine_available(m_id INT)
RETURNS BOOLEAN AS $$
DECLARE 
    status VARCHAR(50);
BEGIN
    SELECT current_status INTO status
    FROM Laundry_Machine
    WHERE machine_id = m_id;
    
    IF status = 'Available' THEN
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function 3: calculate_discount
CREATE OR REPLACE FUNCTION calculate_discount(original_price DECIMAL, discount_percent INT)
RETURNS DECIMAL AS $$
BEGIN
    RETURN original_price - (original_price * discount_percent / 100);
END;
$$ LANGUAGE plpgsql;

-- ==========================================
-- LAYER 3: DATABASE TRIGGERS
-- ==========================================

-- Ensure usage_count exists on Laundry_Machine
ALTER TABLE Laundry_Machine ADD COLUMN IF NOT EXISTS usage_count INT DEFAULT 0;

-- Trigger 1: trg_apply_payment
CREATE OR REPLACE FUNCTION update_wallet_on_transaction()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE Cash_Wallet 
    SET balance = balance + NEW.amount, 
        last_updated = CURRENT_TIMESTAMP 
    WHERE student_id = NEW.student_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_apply_payment ON Wallet_Transaction;
CREATE TRIGGER trg_apply_payment
AFTER INSERT ON Wallet_Transaction
FOR EACH ROW
EXECUTE FUNCTION update_wallet_on_transaction();

-- Trigger 2: trg_machine_start
CREATE OR REPLACE FUNCTION set_machine_busy()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE Laundry_Machine 
    SET current_status = 'Busy' 
    WHERE machine_id = NEW.machine_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_machine_start ON Laundry_Order;
CREATE TRIGGER trg_machine_start
AFTER INSERT ON Laundry_Order
FOR EACH ROW
EXECUTE FUNCTION set_machine_busy();

-- Trigger 3: trg_count_usage
CREATE OR REPLACE FUNCTION increment_machine_usage()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE Laundry_Machine 
    SET usage_count = usage_count + 1 
    WHERE machine_id = NEW.machine_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_count_usage ON Laundry_Order;
CREATE TRIGGER trg_count_usage
AFTER INSERT ON Laundry_Order
FOR EACH ROW
EXECUTE FUNCTION increment_machine_usage();
