import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "E-Commerce API")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Railway automatically injects MYSQLHOST, MYSQLPORT, MYSQLUSER, MYSQLPASSWORD, MYSQLDATABASE
    MYSQL_HOST = os.getenv("MYSQLHOST", os.getenv("MYSQL_HOST", "localhost"))
    MYSQL_PORT = int(os.getenv("MYSQLPORT", os.getenv("MYSQL_PORT", "3306")))
    MYSQL_USER = os.getenv("MYSQLUSER", os.getenv("MYSQL_USER", "root"))
    MYSQL_PASSWORD = os.getenv("MYSQLPASSWORD", os.getenv("MYSQL_PASSWORD", "password"))
    MYSQL_DATABASE = os.getenv("MYSQLDATABASE", os.getenv("MYSQL_DATABASE", "ecommerce_db"))

    MYSQL_POOL_NAME = os.getenv("MYSQL_POOL_NAME", "ecommerce_pool")
    MYSQL_POOL_SIZE = int(os.getenv("MYSQL_POOL_SIZE", "5"))
    MYSQL_POOL_RESET_SESSION = os.getenv("MYSQL_POOL_RESET_SESSION", "true").lower() == "true"
    MYSQL_CONNECT_TIMEOUT = int(os.getenv("MYSQL_CONNECT_TIMEOUT", "10"))
    MYSQL_MAX_RETRIES = int(os.getenv("MYSQL_MAX_RETRIES", "3"))
    MYSQL_RETRY_DELAY_SECONDS = float(os.getenv("MYSQL_RETRY_DELAY_SECONDS", "1.5"))
    AUTO_SEED_ON_STARTUP = os.getenv("AUTO_SEED_ON_STARTUP", "true").lower() == "true"

    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "*").split(",")
        if origin.strip()
    ]

    API_PREFIX = "/api"


settings = Settings()