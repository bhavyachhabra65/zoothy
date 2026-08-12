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



Current Modules
---------------
✔ Cheque Printing

Upcoming Modules
----------------
                   Zoothy

             Run your business, simply.


 Money
 ├── Sales
 ├── Expenses
 ├── Payments
 ├── Bills
 └── Cash

 Business
 ├── Customers
 ├── Suppliers
 ├── Products
 └── Inventory

 Documents
 ├── Invoices
 ├── Cheques
 ├── Receipts
 ├── Delivery Notes
 └── Purchase Orders

 Insights
 ├── Business Reports
 └── Tax

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