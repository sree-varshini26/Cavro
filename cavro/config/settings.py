"""
Configuration settings for the Cavro Resume Agent application.

This file contains all the configuration variables needed for the application.
Sensitive information should be loaded from environment variables in production.
"""
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
# Load .env if python-dotenv is available
try:
    from dotenv import load_dotenv
    _HAS_DOTENV = True
except Exception:
    _HAS_DOTENV = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
if _HAS_DOTENV:
    load_dotenv()
else:
    logging.getLogger(__name__).warning("python-dotenv not installed; skipping .env loading")

# ============================================
# Application Settings
# ============================================
APP_NAME = "Cavro Resume Agent"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development, testing, production

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# API Configuration
# ============================================
# Google Gemini API (Primary AI Provider)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY is not set. AI rewriting features will be disabled.")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")
GEMINI_SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    }
]

# ============================================
# File Handling
# ============================================
# File size limits (in bytes)
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 10))
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes

# Supported file formats
SUPPORTED_FORMATS = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "doc": "application/msword",
    "odt": "application/vnd.oasis.opendocument.text",
    "rtf": "application/rtf",
    "txt": "text/plain",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "tiff": "image/tiff",
    "bmp": "image/bmp"
}

# Allowed file extensions for upload (derived from SUPPORTED_FORMATS)
ALLOWED_EXTENSIONS = list(SUPPORTED_FORMATS.keys())

# ============================================
# Resume Processing
# ============================================
# Resume parsing settings
RESUME_PARSER_SETTINGS = {
    "extract_metadata": True,
    "extract_text": True,
    "clean_text": True,
    "normalize_dates": True,
    "extract_skills": True,
    "extract_experience": True,
    "extract_education": True,
    "extract_contact_info": True,
    "max_workers": 4,  # Number of worker threads for parallel processing
}

# ATS (Applicant Tracking System) scoring settings
ATS_SCORING_SETTINGS = {
    "required_keywords": ["python", "machine learning", "data analysis"],
    "preferred_keywords": ["deep learning", "nlp", "computer vision"],
    "min_keyword_matches": 5,
    "max_keywords_considered": 50,
    "experience_weight": 0.4,
    "skills_weight": 0.3,
    "education_weight": 0.2,
    "keywords_weight": 0.1,
}

# Job description matching settings
JD_MATCHING_SETTINGS = {
    "use_semantic_matching": True,
    "semantic_threshold": 0.7,
    "keyword_weight": 0.6,
    "semantic_weight": 0.4,
    "min_confidence": 0.5,
    "max_keywords": 20,
}

# Resume rewriting settings
RESUME_REWRITER_SETTINGS = {
    "model": "gpt-4-turbo",
    "temperature": 0.7,
    "max_tokens": 2000,
    "style": "professional",
    "include_summary": True,
    "max_bullet_points": 5,
    "max_skills": 15,
    "custom_instructions": "",
}

# Interview preparation settings
INTERVIEW_PREP_SETTINGS = {
    "num_questions": 10,
    "difficulty_levels": ["easy", "medium", "hard"],
    "default_difficulty": "medium",
    "include_answers": True,
    "include_tips": True,
    "max_questions_per_category": 5,
}

# Career suggestions settings
CAREER_SUGGESTIONS_SETTINGS = {
    "max_suggestions": 5,
    "include_salaries": True,
    "include_skills_gap": True,
    "include_learning_path": True,
    "min_confidence": 0.6,
}

# ============================================
# Blockchain Verification
# ============================================
BLOCKCHAIN_SETTINGS = {
    "enabled": True,
    "difficulty": 2,  # Lower is easier (for testing)
    "verify_on_upload": True,
    "verification_expiry_days": 365,  # How long verifications are considered valid
}

# ============================================
# Storage
# ============================================
# File storage settings
STORAGE_SETTINGS = {
    "local_storage_path": os.path.join(BASE_DIR, "storage"),
    "use_cloud_storage": False,
    "cloud_provider": "aws_s3",  # aws_s3, google_cloud, azure_blob
    "temp_dir": os.path.join(BASE_DIR, "temp"),
    "max_temp_files": 100,
    "cleanup_temp_files": True,
}

# ============================================
# Caching
# ============================================
CACHE_SETTINGS = {
    "enabled": True,
    "backend": "memory",  # memory, redis, memcached
    "ttl": 3600,  # Time to live in seconds
    "max_size": 1000,  # Maximum number of items in cache
}

# ============================================
# Logging
# ============================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.path.join(BASE_DIR, "logs", "app.log")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# ============================================
# Security
# ============================================
SECURITY_SETTINGS = {
    "secret_key": os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
    "password_salt_rounds": 10,
    "token_expire_minutes": 1440,  # 24 hours
    "rate_limit": "1000/day",
    "cors_allowed_origins": ["*"],  # In production, replace with actual domains
    "https_only": ENVIRONMENT == "production",
}

# ============================================
# Performance
# ============================================
PERFORMANCE_SETTINGS = {
    "enable_compression": True,
    "cache_timeout": 300,  # 5 minutes
    "max_workers": 4,
    "timeout": 30,  # seconds
}

# ============================================
# Email Settings
# ============================================
EMAIL_SETTINGS = {
    "enabled": False,
    "host": "smtp.gmail.com",
    "port": 587,
    "use_tls": True,
    "username": os.getenv("EMAIL_USERNAME", ""),
    "password": os.getenv("EMAIL_PASSWORD", ""),
    "from_email": "noreply@cavro.ai",
    "from_name": "Cavro Resume Agent",
}

# ============================================
# Feature Flags
# ============================================
FEATURE_FLAGS = {
    "enable_ai_rewrite": bool(GEMINI_API_KEY),
    "enable_blockchain_verification": True,
    "enable_interview_prep": True,
    "enable_career_suggestions": True,
    "enable_ats_scoring": True,
    "enable_job_matching": True,
}

# ============================================
# Constants
# ============================================
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# ============================================
# Environment-specific overrides
# ============================================
if ENVIRONMENT == "production":
    DEBUG = False
    SECURITY_SETTINGS["cors_allowed_origins"] = ["https://your-production-domain.com"]
    SECURITY_SETTINGS["https_only"] = True
    CACHE_SETTINGS["backend"] = "redis"
    STORAGE_SETTINGS["use_cloud_storage"] = True

elif ENVIRONMENT == "testing":
    DEBUG = True
    SECURITY_SETTINGS["cors_allowed_origins"] = ["*"]
    CACHE_SETTINGS["enabled"] = False
    FEATURE_FLAGS["enable_blockchain_verification"] = False

# Create necessary directories
os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)
os.makedirs(STORAGE_SETTINGS["local_storage_path"], exist_ok=True)
os.makedirs(STORAGE_SETTINGS["temp_dir"], exist_ok=True)
