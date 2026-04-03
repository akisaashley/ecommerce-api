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

SEED_SQL = [
    """
    INSERT INTO users (uuid, email, full_name, status)
    VALUES
        ('550e8400-e29b-41d4-a716-446655440000', 'john.doe@example.com', 'John Doe', 'active'),
        ('550e8400-e29b-41d4-a716-446655440001', 'jane.smith@example.com', 'Jane Smith', 'active'),
        ('550e8400-e29b-41d4-a716-446655440002', 'bob.johnson@example.com', 'Bob Johnson', 'active'),
        ('550e8400-e29b-41d4-a716-446655440003', 'alice.williams@example.com', 'Alice Williams', 'active'),
        ('550e8400-e29b-41d4-a716-446655440004', 'charlie.brown@example.com', 'Charlie Brown', 'active')
    ON DUPLICATE KEY UPDATE
        full_name = VALUES(full_name),
        status = VALUES(status)
    """,
    """
    INSERT INTO products (sku, name, description, price, stock_quantity, status)
    VALUES
        ('SKU001', 'Laptop Pro', 'High-performance laptop with 16GB RAM, 512GB SSD', 1299.99, 50, 'active'),
        ('SKU002', 'Wireless Mouse', 'Ergonomic wireless mouse with 2.4GHz connection', 29.99, 200, 'active'),
        ('SKU003', 'Mechanical Keyboard', 'RGB mechanical keyboard with blue switches', 89.99, 150, 'active'),
        ('SKU004', 'USB-C Hub', '7-in-1 USB-C hub with 4K HDMI output', 49.99, 100, 'active'),
        ('SKU005', 'Noise Cancelling Headphones', 'Premium noise cancelling headphones with 30hr battery', 199.99, 75, 'active'),
        ('SKU006', 'Smartphone Stand', 'Adjustable aluminum smartphone stand', 19.99, 300, 'active'),
        ('SKU007', 'External SSD 1TB', 'Portable 1TB SSD with USB 3.2', 119.99, 45, 'active'),
        ('SKU008', 'Webcam HD', '1080p HD webcam with built-in microphone', 79.99, 60, 'active')
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        description = VALUES(description),
        price = VALUES(price),
        stock_quantity = VALUES(stock_quantity)
    """
]


def initialize_database():
    """
    Creates all required tables automatically when the application starts.
    Safe to run multiple times because it uses IF NOT EXISTS and UPSERT-style seeding.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            for statement in SCHEMA_SQL:
                cursor.execute(statement)

            if settings.AUTO_SEED_ON_STARTUP:
                for statement in SEED_SQL:
                    cursor.execute(statement)

            conn.commit()

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