-- Q1 — Which machine had the most downtime last month?
SELECT
    m.machine_id,
    m.machine_code,
    m.machine_name,
    m.machine_type,
    SUM(de.duration_minutes) AS total_downtime_minutes
FROM downtime_events de
JOIN machines m ON de.machine_id = m.machine_id
WHERE de.start_time >= DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 MONTH), '%Y-%m-01')
  AND de.start_time <  DATE_FORMAT(NOW(), '%Y-%m-01')
  AND de.duration_minutes IS NOT NULL
GROUP BY m.machine_id, m.machine_code, m.machine_name, m.machine_type
ORDER BY total_downtime_minutes DESC
LIMIT 1;

-- Q2 — What is the current inventory level for all items below reorder level?

SELECT
    item_code,
    item_name,
    category,
    warehouse_location,
    quantity_in_stock,
    reorder_level,
    (reorder_level - quantity_in_stock) AS shortage
FROM inventory
WHERE quantity_in_stock < reorder_level
  AND status = 'Active'
ORDER BY shortage DESC;

-- Show me all open work orders older than 7 days

SELECT
    wo.work_order_number,
    m.machine_code,
    m.machine_name,
    wo.product_name,
    wo.priority,
    wo.start_time,
    DATEDIFF(NOW(), wo.start_time) AS days_open
FROM work_orders wo
JOIN machines m ON wo.machine_id = m.machine_id
WHERE wo.status = 'Open'
  AND wo.start_time < DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY days_open DESC;


-- Q4 — Which supplier has the worst on-time delivery rate?

SELECT
    s.supplier_code,
    s.supplier_name,
    s.country,
    COUNT(po.po_id)                                              AS total_delivered,
    SUM(CASE
        WHEN po.actual_delivery_date > po.expected_delivery_date
        THEN 1 ELSE 0
    END)                                                         AS late_deliveries,
    ROUND(
        SUM(CASE
            WHEN po.actual_delivery_date > po.expected_delivery_date
            THEN 1 ELSE 0
        END) * 100.0 / COUNT(po.po_id), 2
    )                                                            AS late_rate_pct
FROM purchase_orders po
JOIN suppliers s ON po.supplier_id = s.supplier_id
WHERE po.status = 'Delivered'
GROUP BY s.supplier_id, s.supplier_code, s.supplier_name, s.country
ORDER BY late_rate_pct DESC
LIMIT 5;

-- Q5 — How many quality check failures happened per machine this quarter?

SELECT
    m.machine_code,
    m.machine_name,
    m.machine_type,
    COUNT(qc.check_id) AS failure_count
FROM quality_checks qc
JOIN machines m ON qc.machine_id = m.machine_id
WHERE qc.result = 'Fail'
  AND qc.inspection_date >= DATE_FORMAT(
        MAKEDATE(YEAR(NOW()),1) + INTERVAL (QUARTER(NOW())-1)*3 MONTH,
        '%Y-%m-01'
      )
GROUP BY m.machine_id, m.machine_code, m.machine_name, m.machine_type
ORDER BY failure_count DESC;

-- Q6 — Which technician resolved the most maintenance issues?

SELECT
    e.employee_code,
    e.employee_name,
    e.department,
    COUNT(ml.log_id) AS resolved_count
FROM maintenance_logs ml
JOIN employees e ON ml.employee_id = e.employee_id
WHERE ml.status = 'Resolved'
  AND e.role = 'Technician'
GROUP BY e.employee_id, e.employee_code, e.employee_name, e.department
ORDER BY resolved_count DESC
LIMIT 5;

-- Q7 — What is the average downtime duration per machine type?

SELECT
    m.machine_type,
    COUNT(de.event_id)                        AS total_events,
    ROUND(AVG(de.duration_minutes), 2)        AS avg_duration_minutes,
    ROUND(AVG(de.duration_minutes) / 60, 2)   AS avg_duration_hours,
    SUM(de.duration_minutes)                  AS total_downtime_minutes
FROM downtime_events de
JOIN machines m ON de.machine_id = m.machine_id
WHERE de.duration_minutes IS NOT NULL
GROUP BY m.machine_type
ORDER BY avg_duration_minutes DESC;

-- Q8 — Which warehouse location has the lowest stock levels?

SELECT
    warehouse_location,
    COUNT(item_id)              AS total_items,
    SUM(quantity_in_stock)      AS total_stock,
    ROUND(AVG(quantity_in_stock), 2) AS avg_stock_per_item,
    SUM(CASE
        WHEN quantity_in_stock < reorder_level
        THEN 1 ELSE 0
    END)                        AS items_below_reorder
FROM inventory
WHERE status = 'Active'
GROUP BY warehouse_location
ORDER BY total_stock ASC;

-- Q9 — How many work orders were completed vs pending last week?

SELECT
    status,
    COUNT(order_id) AS work_order_count
FROM work_orders
WHERE start_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
  AND status IN ('Completed', 'Open', 'In Progress')
GROUP BY status
ORDER BY work_order_count DESC;

-- Q10 — Show me the trend of defects over the last 6 months

SELECT
    DATE_FORMAT(inspection_date, '%Y-%m')   AS month,
    COUNT(check_id)                         AS total_inspections,
    SUM(CASE WHEN result = 'Fail' THEN 1 ELSE 0 END) AS total_failures,
    ROUND(
        SUM(CASE WHEN result = 'Fail' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(check_id), 2
    )                                       AS failure_rate_pct
FROM quality_checks
WHERE inspection_date >= (NOW() - INTERVAL 6 MONTH)
GROUP BY DATE_FORMAT(inspection_date, '%Y-%m')
ORDER BY month ASC;