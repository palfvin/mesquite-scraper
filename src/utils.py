import logging
import sys
from typing import Optional


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Sets up logging configuration for the scraper.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("mesquite_scraper")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger


def safe_get_text(element) -> str:
    """
    Safely extracts text from a web element.
    
    Args:
        element: Selenium WebElement
        
    Returns:
        Text content or empty string if extraction fails
    """
    try:
        return element.text.strip() if element else ""
    except Exception:
        return ""


def safe_get_attribute(element, attribute: str) -> str:
    """
    Safely extracts an attribute from a web element.
    
    Args:
        element: Selenium WebElement
        attribute: Attribute name to extract
        
    Returns:
        Attribute value or empty string if extraction fails
    """
    try:
        return element.get_attribute(attribute) if element else ""
    except Exception:
        return ""