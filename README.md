E-Commerce API
A complete, production-ready E-Commerce API built with:

Backend: FastAPI (Python 3.11)

Database: MySQL 8.0

Frontend: Responsive HTML/CSS/JavaScript

Deployment: Railway

Containerization: Docker

Local Development: Docker Compose

Student / Developer Details
Name: Akisa Ashley Maria

Student Number: 2300705729

Reg Number: 23/U/5729

Institution: Makerere University

Programme Context: Software Engineering Student

Features
Products
List products with pagination

Filter products by minimum stock quantity

Search products by name or SKU

Get single product details

Check stock availability for specific quantity

Orders
Create order with transaction support

Automatic stock validation before order creation

Real-time stock deduction

Inventory transaction logging

List orders with user filtering

Get order details with line items

Database / Monitoring
Connection pooling for efficient database access

ACID transaction compliance

Auto database table creation on startup

Auto seed data (5 users, 8 products)

Health check endpoint with database status

Request/response logging middleware

JSON-formatted structured logs

Project Structure
bash
ecommerce-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── mysql_connector.py
│   │   └── db_initializer.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── products.py
│   │   └── orders.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── user.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── logging.py
│   └── static/
│       └── index.html
├── requirements.txt
├── Dockerfile
├── railway.json
├── docker-compose.yml
├── init_db.sql
├── .env.example
├── .gitignore
├── .dockerignore
└── README.md