SELECT COUNT(*) FROM machines;
SELECT COUNT(*) FROM employees;
SELECT COUNT(*) FROM suppliers;
SELECT COUNT(*) FROM inventory;



-- Step 1: Disable FK checks
SET FOREIGN_KEY_CHECKS = 0;

-- Step 2: Truncate all 4 master tables
TRUNCATE TABLE quality_checks;
TRUNCATE TABLE shift_logs;
TRUNCATE TABLE purchase_orders;
TRUNCATE TABLE downtime_events;
TRUNCATE TABLE maintenance_logs;
TRUNCATE TABLE work_orders;
TRUNCATE TABLE inventory;
TRUNCATE TABLE suppliers;
TRUNCATE TABLE employees;
TRUNCATE TABLE machines;

-- Step 3: Re-enable FK checks immediately
SET FOREIGN_KEY_CHECKS = 1;


ALTER TABLE suppliers
MODIFY COLUMN contact_phone VARCHAR(30);

DESC suppliers;