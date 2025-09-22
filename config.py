import os
import logging

class Config:
    METRO_API_URL = "https://api.xor.cl/red/metro-network"
    REQUEST_TIMEOUT = 10
    MAX_RETRIES = 3

    # Flask settings
    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", 8080))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # Logging
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = logging.WARNING

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG

def get_config():
    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        return ProductionConfig()
    return DevelopmentConfig()