from app.config import settings
from app.database.mysql_connector import get_db_connection
from app.middleware.logging import app_logger, log_json

SCHEMA_SQL = [
    """
    CREATE TABLE IF NOT EXISTS users (
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
    CREATE TABLE IF NOT EXISTS products (
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
    CREATE TABLE IF NOT EXISTS orders (
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
    CREATE TABLE IF NOT EXISTS order_items (
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
    CREATE TABLE IF NOT EXISTS inventory_transactions (
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

# Drop existing problematic columns if they exist
DROP_COLUMNS_SQL = [
    "ALTER TABLE users DROP COLUMN IF EXISTS status",
    "ALTER TABLE products DROP COLUMN IF EXISTS status",
]

# Seed data without status column
SEED_SQL = [
    """
    INSERT INTO users (uuid, email, full_name)
    SELECT * FROM (SELECT 
        '550e8400-e29b-41d4-a716-446655440000', 'john.doe@example.com', 'John Doe'
    ) AS tmp
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'john.doe@example.com')
    """,
    """
    INSERT INTO users (uuid, email, full_name)
    SELECT * FROM (SELECT 
        '550e8400-e29b-41d4-a716-446655440001', 'jane.smith@example.com', 'Jane Smith'
    ) AS tmp
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'jane.smith@example.com')
    """,
    """
    INSERT INTO users (uuid, email, full_name)
    SELECT * FROM (SELECT 
        '550e8400-e29b-41d4-a716-446655440002', 'bob.johnson@example.com', 'Bob Johnson'
    ) AS tmp
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'bob.johnson@example.com')
    """,
    """
    INSERT INTO users (uuid, email, full_name)
    SELECT * FROM (SELECT 
        '550e8400-e29b-41d4-a716-446655440003', 'alice.williams@example.com', 'Alice Williams'
    ) AS tmp
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'alice.williams@example.com')
    """,
    """
    INSERT INTO users (uuid, email, full_name)
    SELECT * FROM (SELECT 
        '550e8400-e29b-41d4-a716-446655440004', 'charlie.brown@example.com', 'Charlie Brown'
    ) AS tmp
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'charlie.brown@example.com')
    """,
    """
    INSERT INTO products (sku, name, description, price, stock_quantity)
    SELECT * FROM (SELECT 'SKU001', 'Laptop Pro', 'High-performance laptop with 16GB RAM, 512GB SSD', 1299.99, 50) AS tmp
    WHERE NOT EXISTS (SELECT 1 FROM products WHERE sku = 'SKU001')
    """,
    """
    INSERT INTO products (sku, name, description, price, stock_quantity)
    SELECT * FROM (SELECT 'SKU002', 'Wireless Mouse', 'Ergonomic wireless mouse with 2.4GHz connection', 29.99, 200) AS tmp
    WHERE NOT EXISTS (SELECT 1 FROM products WHERE sku = 'SKU002')
    """,
    """
    INSERT INTO products (sku, name, description, price, stock_quantity)
    SELECT * FROM (SELECT 'SKU003', 'Mechanical Keyboard', 'RGB mechanical keyboard with blue switches', 89.99, 150) AS tmp
    WHERE NOT EXISTS (SELECT 1 FROM products WHERE sku = 'SKU003')
    """,
    """
    INSERT INTO products (sku, name, description, price, stock_quantity)
    SELECT * FROM (SELECT 'SKU004', 'USB-C Hub', '7-in-1 USB-C hub with 4K HDMI output', 49.99, 100) AS tmp
    WHERE NOT EXISTS (SELECT 1 FROM products WHERE sku = 'SKU004')
    """,
    """
    INSERT INTO products (sku, name, description, price, stock_quantity)
    SELECT * FROM (SELECT 'SKU005', 'Noise Cancelling Headphones', 'Premium noise cancelling headphones with 30hr battery', 199.99, 75) AS tmp
    WHERE NOT EXISTS (SELECT 1 FROM products WHERE sku = 'SKU005')
    """,
    """
    INSERT INTO products (sku, name, description, price, stock_quantity)
    SELECT * FROM (SELECT 'SKU006', 'Smartphone Stand', 'Adjustable aluminum smartphone stand', 19.99, 300) AS tmp
    WHERE NOT EXISTS (SELECT 1 FROM products WHERE sku = 'SKU006')
    """,
    """
    INSERT INTO products (sku, name, description, price, stock_quantity)
    SELECT * FROM (SELECT 'SKU007', 'External SSD 1TB', 'Portable 1TB SSD with USB 3.2', 119.99, 45) AS tmp
    WHERE NOT EXISTS (SELECT 1 FROM products WHERE sku = 'SKU007')
    """,
    """
    INSERT INTO products (sku, name, description, price, stock_quantity)
    SELECT * FROM (SELECT 'SKU008', 'Webcam HD', '1080p HD webcam with built-in microphone', 79.99, 60) AS tmp
    WHERE NOT EXISTS (SELECT 1 FROM products WHERE sku = 'SKU008')
    """,
]


def initialize_database():
    """
    Creates all required tables automatically when the application starts.
    Safe to run multiple times because it uses IF NOT EXISTS.
    """
    log_json("info", "database_initialization_started")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            # Create tables
            for statement in SCHEMA_SQL:
                cursor.execute(statement)
                log_json("info", "schema_statement_executed", statement_preview=statement[:100])

            conn.commit()
            
            # Try to drop status columns if they exist (ignore errors)
            for statement in DROP_COLUMNS_SQL:
                try:
                    cursor.execute(statement)
                    conn.commit()
                    log_json("info", "dropped_status_column", table=statement.split()[2])
                except Exception as e:
                    # Column might not exist, that's fine
                    pass

            # Seed data if enabled
            if settings.AUTO_SEED_ON_STARTUP:
                for statement in SEED_SQL:
                    cursor.execute(statement)
                    log_json("info", "seed_statement_executed", statement_preview=statement[:80])
                
                conn.commit()
                log_json("info", "seed_data_inserted")

            log_json(
                "info",
                "database_initialized",
                message="Database tables verified/created successfully on startup"
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