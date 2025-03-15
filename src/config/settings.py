import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Settings
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"
PROJECT_NAME = "Decentralized Medical Data Management"

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medical_data.db")

# Blockchain settings
BLOCKCHAIN_PROVIDER = os.getenv("BLOCKCHAIN_PROVIDER", "http://localhost:8545")
CHAIN_ID = int(os.getenv("CHAIN_ID", "1"))
GAS_LIMIT = int(os.getenv("GAS_LIMIT", "3000000"))
GAS_PRICE = int(os.getenv("GAS_PRICE", "20000000000"))

# AI Model settings
MODEL_SETTINGS: Dict[str, Any] = {
    "input_size": 64,
    "hidden_size": 128,
    "num_classes": 5,
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 100,
}

# Encryption settings
ENCRYPTION_KEY_LENGTH = 32
SALT_LENGTH = 16
HASH_ITERATIONS = 100000

# Access Control settings
DEFAULT_ACCESS_DURATION_DAYS = 30
MAX_ACCESS_DURATION_DAYS = 365

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Cache settings
CACHE_TTL = 300  # 5 minutes
CACHE_MAX_SIZE = 1000

# Rate limiting
RATE_LIMIT_PER_MINUTE = 60

# File upload settings
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "dcm"}  # DICOM and common formats

# Notification settings
ENABLE_EMAIL_NOTIFICATIONS = bool(os.getenv("ENABLE_EMAIL_NOTIFICATIONS", False))
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Smart contract addresses
CONTRACT_ADDRESSES = {
    "medical_records": os.getenv("MEDICAL_RECORDS_CONTRACT", ""),
    "access_control": os.getenv("ACCESS_CONTROL_CONTRACT", ""),
}

# CORS settings
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

# Health check settings
HEALTH_CHECK_INTERVAL = 30  # seconds

# Cleanup settings
DATA_RETENTION_DAYS = 365  # 1 year
CLEANUP_INTERVAL_HOURS = 24

# Feature flags
FEATURES = {
    "ai_analysis": bool(os.getenv("ENABLE_AI_ANALYSIS", True)),
    "blockchain_storage": bool(os.getenv("ENABLE_BLOCKCHAIN_STORAGE", True)),
    "data_encryption": bool(os.getenv("ENABLE_DATA_ENCRYPTION", True)),
    "access_control": bool(os.getenv("ENABLE_ACCESS_CONTROL", True)),
}
