# AI Agent for Operational Database

## Overview

AI Agent for Operational Database is an intelligent manufacturing analytics platform designed to enable natural language interaction with operational data.

The system combines a structured operational database, synthetic data generation pipelines, and AI-driven query capabilities to help users retrieve business insights through conversational queries without writing SQL.

The project focuses on manufacturing operations, covering production, maintenance, inventory, procurement, workforce management, downtime analysis, and quality control.

---

## Problem Statement

Manufacturing organizations generate large volumes of operational data across multiple systems, including production tracking, maintenance management, inventory control, supplier management, and quality assurance.

Accessing business insights typically requires manual SQL queries, dashboard development, or technical expertise.

This project aims to bridge that gap by building an AI-powered agent capable of understanding natural language questions and retrieving relevant operational insights directly from a structured database.

---

## Objectives

- Design a production-oriented operational database schema
- Model manufacturing business processes using relational databases
- Generate realistic synthetic operational datasets
- Enable analytical querying across multiple business domains
- Build an AI-powered natural language interface for database interaction
- Support operational decision-making through conversational analytics

---

## System Architecture

```text
User Query
     │
     ▼
AI Agent Layer
     │
     ▼
Text-to-SQL Engine
     │
     ▼
MySQL Operational Database
     │
     ▼
Manufacturing Business Data
```

---

## Technology Stack

### Database

- MySQL
- MySQL Workbench

### Data Generation

- Python
- Faker

### AI Layer (Planned)

- Large Language Models (LLMs)
- Text-to-SQL Pipeline
- Query Validation Layer

### Development Tools

- Git
- GitHub
- DrawDB / DBML
- Visual Studio Code

---

## Database Design

The operational database consists of:

### Master Tables

1. Machines
2. Employees
3. Suppliers
4. Inventory

### Transactional Tables

5. Work Orders
6. Maintenance Logs
7. Downtime Events
8. Purchase Orders
9. Shift Logs
10. Quality Checks

---

## Key Features

### Operational Tracking

- Production monitoring
- Work order management
- Machine lifecycle tracking

### Maintenance Analytics

- Maintenance history
- Downtime analysis
- Technician performance evaluation

### Inventory Management

- Stock monitoring
- Reorder analysis
- Warehouse tracking

### Supplier Management

- Lead-time analysis
- Supplier reliability evaluation
- Procurement monitoring

### Quality Assurance

- Inspection tracking
- Defect analysis
- Quality trend reporting

### Workforce Management

- Employee tracking
- Shift management
- Operational workforce analytics

---

## Sprint Progress

### Sprint 1 — Database Design & Schema

Completed:

- Business requirements analysis
- Entity identification
- ERD design
- Primary key design
- Foreign key design
- Database normalization
- MySQL schema implementation
- Constraint definition
- Indexing strategy
- Database validation

Deliverables:

- ERD Diagram
- MySQL Schema
- Database Documentation
- Validation Queries

---

## Planned Development Roadmap

### Sprint 2

- Synthetic data generation using Faker
- Foreign key consistency validation
- Bulk data insertion scripts
- Dataset verification

### Sprint 3

- Analytical SQL query development
- Business KPI generation
- Query optimization

### Sprint 4

- AI Agent integration
- Natural Language to SQL conversion
- Query validation layer

### Sprint 5

- End-to-end system integration
- Testing and evaluation

---

## Example Business Questions

The system is designed to answer questions such as:

- Which machine experienced the highest downtime?
- Which inventory items are below reorder level?
- Which supplier has the worst delivery performance?
- What are the most common maintenance issues?
- Which machines generate the most quality defects?
- What is the average downtime by machine type?
- Which employees resolve maintenance issues most efficiently?

---

## Repository Structure

```text
AI-Agent-Operational-Database/
│
├── database/
│   ├── schema_v1.sql
│   ├── master_tables.sql
│   ├── transactional_tables.sql
│   └── verification_queries.sql
│
├── docs/
│   ├── erd/
│   ├── sprint_reports/
│   └── architecture/
│
├── data_generation/
│
├── agent/
│
└── README.md
```

---

## Current Status

**Sprint 1 Completed**

- ERD finalized
- Schema implemented
- Database deployed in MySQL
- All 10 tables created successfully

Next milestone: Synthetic data generation and database population.

---

## Author

**Ajas Muhammed N**

M.Tech Artificial Intelligence  
TKM College of Engineering

Internship Project — AI Agent for Operational Database
