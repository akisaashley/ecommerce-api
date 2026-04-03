from app.config import settings
from app.database.mysql_connector import get_db_connection
from app.middleware.logging import app_logger, log_json

# Drop tables in reverse order (to handle foreign keys)
DROP_TABLES_SQL = [
    "DROP TABLE IF EXISTS inventory_transactions",
    "DROP TABLE IF EXISTS order_items",
    "DROP TABLE IF EXISTS orders",
    "DROP TABLE IF EXISTS products",
    "DROP TABLE IF EXISTS users",
]

# Create tables
SCHEMA_SQL = [
    """
    CREATE TABLE users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        uuid VARCHAR(36) NOT NULL UNIQUE,
        email VARCHAR(255) NOT NULL UNIQUE,
        full_name VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_email (email),
        INDEX idx_uuid (uuid)
    )
    """,
    """
    CREATE TABLE products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sku VARCHAR(100) NOT NULL UNIQUE,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        price DECIMAL(10, 2) NOT NULL,
        stock_quantity INT NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_sku (sku),
        INDEX idx_stock (stock_quantity)
    )
    """,
    """
    CREATE TABLE orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_uuid VARCHAR(36) NOT NULL UNIQUE,
        user_id INT NOT NULL,
        total_amount DECIMAL(10, 2) NOT NULL,
        status ENUM('pending', 'confirmed', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
        INDEX idx_user_id (user_id),
        INDEX idx_status (status),
        INDEX idx_order_uuid (order_uuid)
    )
    """,
    """
    CREATE TABLE order_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        unit_price DECIMAL(10, 2) NOT NULL,
        subtotal DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
        INDEX idx_order_id (order_id),
        INDEX idx_product_id (product_id)
    )
    """,
    """
    CREATE TABLE inventory_transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT NOT NULL,
        transaction_type ENUM('stock_in', 'stock_out', 'adjustment') NOT NULL,
        quantity INT NOT NULL,
        previous_stock INT NOT NULL,
        new_stock INT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
        INDEX idx_product_id (product_id),
        INDEX idx_created_at (created_at)
    )
    """,
]

# Seed data
SEED_USERS = [
    "INSERT INTO users (uuid, email, full_name) VALUES ('550e8400-e29b-41d4-a716-446655440000', 'john.doe@example.com', 'John Doe')",
    "INSERT INTO users (uuid, email, full_name) VALUES ('550e8400-e29b-41d4-a716-446655440001', 'jane.smith@example.com', 'Jane Smith')",
    "INSERT INTO users (uuid, email, full_name) VALUES ('550e8400-e29b-41d4-a716-446655440002', 'bob.johnson@example.com', 'Bob Johnson')",
    "INSERT INTO users (uuid, email, full_name) VALUES ('550e8400-e29b-41d4-a716-446655440003', 'alice.williams@example.com', 'Alice Williams')",
    "INSERT INTO users (uuid, email, full_name) VALUES ('550e8400-e29b-41d4-a716-446655440004', 'charlie.brown@example.com', 'Charlie Brown')",
]

SEED_PRODUCTS = [
    "INSERT INTO products (sku, name, description, price, stock_quantity) VALUES ('SKU001', 'Laptop Pro', 'High-performance laptop with 16GB RAM, 512GB SSD', 1299.99, 50)",
    "INSERT INTO products (sku, name, description, price, stock_quantity) VALUES ('SKU002', 'Wireless Mouse', 'Ergonomic wireless mouse with 2.4GHz connection', 29.99, 200)",
    "INSERT INTO products (sku, name, description, price, stock_quantity) VALUES ('SKU003', 'Mechanical Keyboard', 'RGB mechanical keyboard with blue switches', 89.99, 150)",
    "INSERT INTO products (sku, name, description, price, stock_quantity) VALUES ('SKU004', 'USB-C Hub', '7-in-1 USB-C hub with 4K HDMI output', 49.99, 100)",
    "INSERT INTO products (sku, name, description, price, stock_quantity) VALUES ('SKU005', 'Noise Cancelling Headphones', 'Premium noise cancelling headphones with 30hr battery', 199.99, 75)",
    "INSERT INTO products (sku, name, description, price, stock_quantity) VALUES ('SKU006', 'Smartphone Stand', 'Adjustable aluminum smartphone stand', 19.99, 300)",
    "INSERT INTO products (sku, name, description, price, stock_quantity) VALUES ('SKU007', 'External SSD 1TB', 'Portable 1TB SSD with USB 3.2', 119.99, 45)",
    "INSERT INTO products (sku, name, description, price, stock_quantity) VALUES ('SKU008', 'Webcam HD', '1080p HD webcam with built-in microphone', 79.99, 60)",
]


def initialize_database():
    """
    Drops all existing tables and recreates them fresh.
    This ensures a clean slate on every startup.
    """
    log_json("info", "database_initialization_started")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            # Drop existing tables
            log_json("info", "dropping_existing_tables")
            for statement in DROP_TABLES_SQL:
                cursor.execute(statement)
                log_json("info", "table_dropped", table=statement.split()[2])
            
            conn.commit()
            log_json("info", "all_tables_dropped")

            # Create fresh tables
            log_json("info", "creating_fresh_tables")
            for statement in SCHEMA_SQL:
                cursor.execute(statement)
                log_json("info", "table_created", table=statement.split()[2].split()[0])
            
            conn.commit()
            log_json("info", "all_tables_created")

            # Seed users
            if settings.AUTO_SEED_ON_STARTUP:
                log_json("info", "seeding_users")
                for statement in SEED_USERS:
                    cursor.execute(statement)
                conn.commit()
                log_json("info", "users_seeded", count=len(SEED_USERS))

                # Seed products
                log_json("info", "seeding_products")
                for statement in SEED_PRODUCTS:
                    cursor.execute(statement)
                conn.commit()
                log_json("info", "products_seeded", count=len(SEED_PRODUCTS))

            log_json(
                "info",
                "database_initialized",
                message="Database tables recreated and seeded successfully on startup"
            )
        except Exception as exc:
            conn.rollback()
            app_logger.exception(
                {
                    "event": "database_initialization_failed",
                    "error": str(exc),
                }
            )
            raise
        finally:
            cursor.close()