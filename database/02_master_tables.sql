CREATE TABLE IF NOT EXISTS machines (
    machine_id INT NOT NULL AUTO_INCREMENT,
    machine_code VARCHAR(20) NOT NULL,
    machine_name VARCHAR(100) NOT NULL,
    machine_type VARCHAR(50) NOT NULL,
    production_line VARCHAR(50) NOT NULL,
    location VARCHAR(100) NOT NULL,
    installation_date DATE NOT NULL,

    status ENUM(
        'Active',
        'Maintenance',
        'Retired'
    ) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (machine_id),

    CONSTRAINT uk_machine_code
        UNIQUE (machine_code),

    INDEX idx_machine_type (machine_type),
    INDEX idx_machine_status (status),
    INDEX idx_production_line (production_line)

) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS employees (
    employee_id INT NOT NULL AUTO_INCREMENT,
    employee_code VARCHAR(20) NOT NULL,
    employee_name VARCHAR(100) NOT NULL,

    role ENUM(
        'Technician',
        'Operator',
        'Supervisor',
        'Inspector',
        'Manager'
    ) NOT NULL,

    department VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL,

    status ENUM(
        'Active',
        'Inactive'
    ) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (employee_id),

    CONSTRAINT uk_employee_code
        UNIQUE (employee_code),

    INDEX idx_employee_role (role),
    INDEX idx_employee_department (department),
    INDEX idx_employee_status (status)

) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INT NOT NULL AUTO_INCREMENT,
    supplier_code VARCHAR(20) NOT NULL,
    supplier_name VARCHAR(100) NOT NULL,

    contact_phone VARCHAR(20),
    contact_email VARCHAR(100),

    lead_time_days INT NOT NULL,

    reliability_score DECIMAL(5,2)
        NOT NULL DEFAULT 0.00,

    country VARCHAR(50) NOT NULL,

    status ENUM(
        'Active',
        'Inactive'
    ) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (supplier_id),

    CONSTRAINT uk_supplier_code
        UNIQUE (supplier_code),

    INDEX idx_supplier_name (supplier_name),
    INDEX idx_supplier_country (country),
    INDEX idx_supplier_status (status),
    INDEX idx_supplier_reliability (reliability_score)

) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS inventory (
    item_id INT NOT NULL AUTO_INCREMENT,
    item_code VARCHAR(20) NOT NULL,
    item_name VARCHAR(100) NOT NULL,

    category ENUM(
        'Raw Material',
        'Component',
        'Finished Good'
    ) NOT NULL,

    quantity_in_stock INT NOT NULL,

    warehouse_location VARCHAR(50) NOT NULL,

    reorder_level INT NOT NULL,

    unit_of_measure VARCHAR(20) NOT NULL,

    status ENUM(
        'Active',
        'Discontinued'
    ) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (item_id),

    CONSTRAINT uk_item_code
        UNIQUE (item_code),

    INDEX idx_inventory_category (category),
    INDEX idx_inventory_warehouse (warehouse_location),
    INDEX idx_inventory_stock (quantity_in_stock),
    INDEX idx_inventory_reorder (reorder_level),
    INDEX idx_inventory_status (status)

) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;

Show TABLES;

DESCRIBE machines;
DESCRIBE employees;
DESCRIBE suppliers;
DESCRIBE inventory;