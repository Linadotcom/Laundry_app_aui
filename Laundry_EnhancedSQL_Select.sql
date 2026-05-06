-- Purpose:
-- Shows all laundry orders received on a specific day, including:
    -- Student details
    -- Residence
    -- Service type
    -- Price
    -- Staff handling the order

-- This query allows laundry staff to monitor all orders dropped off on a given date, helping daily workflow management.

-- LINA LASSRI
SELECT 
    o.order_id,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    s.residence,
    s.room,
    o.service_type,
    o.weight_kg,
    o.total_price,
    o.order_status,
    CONCAT(st.first_name, ' ', st.last_name) AS processed_by
FROM Laundry_Order o
JOIN Student s ON o.student_id = s.student_id
LEFT JOIN Laundry_Staff st ON o.staff_id = st.staff_id
WHERE DATE(o.dropoff_date) = '2026-03-01';


-- Purpose:
Tracks:
    -- Which machines are in use
    -- Assigned orders
    -- Student owner
    -- Machine location
    -- Order progress

-- This query helps administrators monitor active machines and track which student orders are currently being processed.

-- Salma Essagar
SELECT 
    m.machine_id,
    m.machine_type,
    m.brand_model,
    m.location,
    m.current_status,
    o.order_id,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    o.order_status
FROM Laundry_Machine m
JOIN Laundry_Order o ON m.machine_id = o.machine_id
JOIN Student s ON o.student_id = s.student_id
WHERE m.current_status = 'In Use'
   OR o.order_status = 'In Progress';


-- Purpose:
    -- QR CODE PICKUP VERIFICATION
-- Supports:
    -- Pickup verification
    -- Student identification
    -- QR code retrieval
    -- Expected pickup schedule

-- This query ensures secure order pickup by linking each order to a QR code and customer contact information.

-- Med Ali Kabiri
SELECT 
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    s.phone_number,
    o.order_id,
    q.qr_code_string,
    o.expected_pickup,
    o.order_status
FROM Laundry_Order o
JOIN Student s ON o.student_id = s.student_id
JOIN QR_Code q ON o.order_id = q.order_id
WHERE o.order_status IN ('Ready', 'Pending');

-- Purpose:
    -- Revenue and Service Analysis
--Provides:
    -- Number of orders per service
    --Revenue per service type
    --Operational insights

-- this query analyzes service popularity and revenue generation to support pricing and strategic decisions.

-- Fatima Zahra 
SELECT 
    p.service_type,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_price) AS total_revenue,
    AVG(o.total_price) AS average_order_value
FROM Pricing p
LEFT JOIN Laundry_Order o ON p.service_type = o.service_type
GROUP BY p.service_type;

-- Purpose:
-- This query tracks:

    --Student wallet balances
    --Payment history
    --Transaction amounts
    --Payment types
    --Related laundry orders

-- This query provides a complete financial overview of student wallet balances and payment transactions

-- Med Amine Rais
SELECT 
    s.student_id,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    cw.balance AS current_wallet_balance,
    wt.transaction_id,
    wt.order_id,
    wt.amount,
    wt.transaction_type,
    wt.created_at
FROM Student s
JOIN Cash_Wallet cw ON s.student_id = cw.student_id
LEFT JOIN Wallet_Transaction wt ON s.student_id = wt.student_id
ORDER BY s.student_id, wt.created_at DESC;










