"""
Utility functions for the GDPR RAG system
"""
import yaml
from pathlib import Path
from typing import Dict, Any
from loguru import logger
import sys


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise


def setup_logging(config: Dict[str, Any]) -> None:
    """Setup logging configuration"""
    log_config = config.get('logging', {})
    log_level = log_config.get('level', 'INFO')
    log_file = log_config.get('file', 'logs/gdpr_rag.log')
    log_format = log_config.get('format', '{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}')
    
    # Create logs directory if it doesn't exist
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stderr,
        format=log_format,
        level=log_level,
        colorize=True
    )
    
    # Add file logger
    logger.add(
        log_file,
        format=log_format,
        level=log_level,
        rotation="10 MB",
        retention="1 month",
        compression="zip"
    )


def ensure_directories(base_path: Path = Path(".")):
    """Ensure all required directories exist"""
    directories = [
        "data/raw",
        "data/processed",
        "vectorstore",
        "logs",
        ".cache"
    ]
    
    for directory in directories:
        (base_path / directory).mkdir(parents=True, exist_ok=True)
