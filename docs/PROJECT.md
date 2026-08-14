# Zoothy

we are the complete accounting software for the startup founders, when they have the small team size.

| Traditional         | Zoothy                |
| ------------------- | --------------------- |
| Accounts Receivable | **Money to Collect**  |
| Accounts Payable    | **Bills to Pay**      |
| Expenses            | **Expenses**          |
| Revenue             | **Sales**             |
| General Ledger      | **Business Activity** |
| Customers           | **Customers**         |
| Vendors             | **Suppliers**         |
| Invoices            | **Invoices**          |
| Receipts            | **Payment Receipts**  |
| Bank Reconciliation | **Match Payments**    |
| Reports             | **Business Reports**  |




Current Version
---------------
v1.0.0


Completed Modules
---------------
✔ Dashboard
✔ Cheque Printing


All Modules
----------------

Money
├── Sales
├── Expenses
├── Receive Money
└── Pay Money


Business
├── Customers
├── Suppliers
├── Products
└── Inventory


Documents
├── Invoices
├── Bills
├── Receipts
├── Cheques
├── Delivery Notes
└── Purchase Orders


Reports
├── Overview
├── Sales
├── Expenses
├── Money
├── Customers
├── Suppliers
├── Inventory
├── Tax
└── Accounting


Settings

Technology Stack
----------------
Backend
- Python 3.13
- Flask
- Gunicorn

Frontend
- HTML5
- CSS3
- Vanilla JavaScript

Infrastructure
- Docker
- Docker Compose
- Nginx
- Let's Encrypt SSL

Database
--------
None (Currently)

Future
------
SQLite
PostgreSQL

Design Goals
------------
- Simple
- Fast
- Pixel-perfect printing
- Modular architecture
- No unnecessary dependencies

Principles
----------
- One module = one Flask Blueprint
- Business logic separated from routes
- Printing accuracy over visual complexity
- Consistent UI across all modules