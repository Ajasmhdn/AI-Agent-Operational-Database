CREATE TABLE IF NOT EXISTS work_orders (
    order_id INT NOT NULL AUTO_INCREMENT,
    work_order_number VARCHAR(20) NOT NULL,

    machine_id INT NOT NULL,
    item_id INT NOT NULL,

    product_name VARCHAR(100) NOT NULL,

    quantity_planned INT NOT NULL,
    quantity_completed INT NOT NULL,

    priority ENUM(
        'Low',
        'Medium',
        'High',
        'Critical'
    ) NOT NULL,

    start_time DATETIME NOT NULL,
    end_time DATETIME NULL,

    status ENUM(
        'Open',
        'In Progress',
        'Completed',
        'Cancelled'
    ) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (order_id),

    CONSTRAINT uk_work_order_number
        UNIQUE (work_order_number),

    CONSTRAINT fk_work_orders_machine
        FOREIGN KEY (machine_id)
        REFERENCES machines(machine_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_work_orders_item
        FOREIGN KEY (item_id)
        REFERENCES inventory(item_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_wo_machine (machine_id),
    INDEX idx_wo_item (item_id),
    INDEX idx_wo_status (status),
    INDEX idx_wo_priority (priority),
    INDEX idx_wo_start_time (start_time)

) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS maintenance_logs (
    log_id INT NOT NULL AUTO_INCREMENT,

    log_code VARCHAR(20) NOT NULL,

    machine_id INT NOT NULL,
    employee_id INT NOT NULL,

    issue_type VARCHAR(50) NOT NULL,

    issue_description TEXT NOT NULL,

    reported_time DATETIME NOT NULL,
    resolved_time DATETIME NULL,

    resolution_notes TEXT NULL,

    status ENUM(
        'Open',
        'In Progress',
        'Resolved'
    ) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (log_id),

    CONSTRAINT uk_log_code
        UNIQUE (log_code),

    CONSTRAINT fk_maintenance_machine
        FOREIGN KEY (machine_id)
        REFERENCES machines(machine_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_maintenance_employee
        FOREIGN KEY (employee_id)
        REFERENCES employees(employee_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_maint_machine (machine_id),
    INDEX idx_maint_employee (employee_id),
    INDEX idx_maint_issue_type (issue_type),
    INDEX idx_maint_status (status),
    INDEX idx_maint_reported_time (reported_time),
    INDEX idx_maint_resolved_time (resolved_time)

) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS downtime_events (
    event_id INT NOT NULL AUTO_INCREMENT,

    event_code VARCHAR(20) NOT NULL,

    machine_id INT NOT NULL,

    start_time DATETIME NOT NULL,
    end_time DATETIME NULL,

    duration_minutes INT NULL,

    reason VARCHAR(100) NOT NULL,

    severity ENUM(
        'Low',
        'Medium',
        'High'
    ) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (event_id),

    CONSTRAINT uk_event_code
        UNIQUE (event_code),

    CONSTRAINT fk_downtime_machine
        FOREIGN KEY (machine_id)
        REFERENCES machines(machine_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_downtime_machine (machine_id),
    INDEX idx_downtime_start_time (start_time),
    INDEX idx_downtime_end_time (end_time),
    INDEX idx_downtime_reason (reason),
    INDEX idx_downtime_severity (severity),
    INDEX idx_downtime_duration (duration_minutes)

) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS purchase_orders (
    po_id INT NOT NULL AUTO_INCREMENT,

    po_number VARCHAR(20) NOT NULL,

    supplier_id INT NOT NULL,
    item_id INT NOT NULL,

    quantity INT NOT NULL,

    order_date DATE NOT NULL,

    expected_delivery_date DATE NOT NULL,
    actual_delivery_date DATE NULL,

    status ENUM(
        'Ordered',
        'Delivered',
        'Cancelled'
    ) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (po_id),

    CONSTRAINT uk_po_number
        UNIQUE (po_number),

    CONSTRAINT fk_purchase_supplier
        FOREIGN KEY (supplier_id)
        REFERENCES suppliers(supplier_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_purchase_item
        FOREIGN KEY (item_id)
        REFERENCES inventory(item_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_po_supplier (supplier_id),
    INDEX idx_po_item (item_id),
    INDEX idx_po_status (status),
    INDEX idx_po_order_date (order_date),
    INDEX idx_po_expected_delivery (expected_delivery_date),
    INDEX idx_po_actual_delivery (actual_delivery_date)

) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS shift_logs (
    shift_log_id INT NOT NULL AUTO_INCREMENT,

    shift_code VARCHAR(20) NOT NULL,

    employee_id INT NOT NULL,

    shift_date DATE NOT NULL,

    shift_type ENUM(
        'Day',
        'Evening',
        'Night'
    ) NOT NULL,

    start_time DATETIME NOT NULL,
    end_time DATETIME NULL,

    notes TEXT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (shift_log_id),

    CONSTRAINT uk_shift_code
        UNIQUE (shift_code),

    CONSTRAINT fk_shift_employee
        FOREIGN KEY (employee_id)
        REFERENCES employees(employee_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_shift_employee (employee_id),
    INDEX idx_shift_date (shift_date),
    INDEX idx_shift_type (shift_type),
    INDEX idx_shift_start_time (start_time),
    INDEX idx_shift_end_time (end_time)

) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;


CREATE TABLE IF NOT EXISTS quality_checks (
    check_id INT NOT NULL AUTO_INCREMENT,

    qc_code VARCHAR(20) NOT NULL,

    machine_id INT NOT NULL,
    work_order_id INT NOT NULL,

    product_name VARCHAR(100) NOT NULL,

    result ENUM(
        'Pass',
        'Fail'
    ) NOT NULL,

    defect_type VARCHAR(50) NOT NULL,

    inspection_date DATETIME NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (check_id),

    CONSTRAINT uk_qc_code
        UNIQUE (qc_code),

    CONSTRAINT fk_quality_machine
        FOREIGN KEY (machine_id)
        REFERENCES machines(machine_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_quality_work_order
        FOREIGN KEY (work_order_id)
        REFERENCES work_orders(order_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_qc_machine (machine_id),
    INDEX idx_qc_work_order (work_order_id),
    INDEX idx_qc_result (result),
    INDEX idx_qc_defect_type (defect_type),
    INDEX idx_qc_inspection_date (inspection_date)

) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;

SHOW TABLES;