SELECT
COUNT(*) total,
COUNT(DISTINCT machine_code) unique_codes
FROM machines;


SELECT
COUNT(*) total,
COUNT(DISTINCT employee_code) unique_codes
FROM employees;


SELECT
COUNT(*) total,
COUNT(DISTINCT supplier_code) unique_codes
FROM suppliers;


SELECT
COUNT(*) total,
COUNT(DISTINCT item_code) unique_codes
FROM inventory;


SELECT status, COUNT(*)
FROM machines
GROUP BY status;

SELECT role, COUNT(*)
FROM employees
GROUP BY role;

SELECT status, COUNT(*)
FROM suppliers
GROUP BY status;

SELECT status, COUNT(*)
FROM inventory
GROUP BY status;

SELECT supplier_code,
       reliability_score
FROM suppliers
WHERE supplier_code='SUP-00001';

SELECT
COUNT(*) total_items,

SUM(
CASE
WHEN quantity_in_stock < reorder_level
THEN 1
ELSE 0
END
) below_reorder,

ROUND(
SUM(
CASE
WHEN quantity_in_stock < reorder_level
THEN 1
ELSE 0
END
)*100.0/COUNT(*),
1
) pct

FROM inventory;


SELECT
category,
unit_of_measure,
COUNT(*)
FROM inventory
GROUP BY category,
unit_of_measure
ORDER BY category;