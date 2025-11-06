import logging
import sys
from datetime import datetime

def setup_logger(name: str = "ocr_app") -> logging.Logger:
    """Setup logger with console and file output"""
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter - simple text without emojis for Windows compatibility
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# Global logger instance
app_logger = setup_logger("OCR_WORKFLOW")