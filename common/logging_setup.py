"""
Logging setup and configuration for the Morning Scanner application.

This module provides:
- Standard logging configuration
- File and console handlers
- Timestamps in local timezone
- Log rotation and formatting
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from .config import get_config


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    config_instance: Optional[object] = None
) -> None:
    """
    Setup logging configuration for the application.
    
    This function configures:
    - Log level (from config or parameter)
    - File handler with rotation to storage/errors.log
    - Console handler
    - Standard log format with timestamps in local timezone
    
    Args:
        log_level (str, optional): Override log level from config
        log_file (str, optional): Override log file path from config
        config_instance (object, optional): Configuration object. If None, uses global config.
    """
    # Get configuration
    if config_instance is None:
        config_instance = get_config()
    
    # Determine log level
    level = log_level or getattr(config_instance, 'LOG_LEVEL', 'INFO')
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Determine log file path
    if log_file is None:
        log_file = getattr(config_instance, 'ERROR_LOG_FILE', 'storage/errors.log')
    
    # Create logs directory if it doesn't exist
    log_file_path = Path(log_file)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    # Standard formatter with timestamps in local timezone
    standard_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Detailed formatter for file logging
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file_path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(standard_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set specific logger levels for external libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    # Log the setup
    logger = logging.getLogger(__name__)
    logger.info(f"Logging setup complete - Level: {level}, File: {log_file_path}")
    logger.info(f"Timezone: {getattr(config_instance, 'TZ', 'Unknown')}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name (str): Logger name (usually __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


def set_log_level(level: str) -> None:
    """
    Change the log level for all handlers.
    
    Args:
        level (str): New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    
    # Update root logger level
    root_logger.setLevel(numeric_level)
    
    # Update all handler levels
    for handler in root_logger.handlers:
        handler.setLevel(numeric_level)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Log level changed to: {level}")


def add_file_handler(
    file_path: str,
    level: Optional[str] = None,
    formatter: Optional[logging.Formatter] = None
) -> logging.FileHandler:
    """
    Add an additional file handler to the root logger.
    
    Args:
        file_path (str): Path to log file
        level (str, optional): Log level for this handler
        formatter (logging.Formatter, optional): Custom formatter
        
    Returns:
        logging.FileHandler: The created file handler
    """
    # Create directory if it doesn't exist
    log_path = Path(file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create file handler
    file_handler = logging.FileHandler(
        filename=file_path,
        encoding='utf-8'
    )
    
    # Set level
    if level:
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        file_handler.setLevel(numeric_level)
    else:
        file_handler.setLevel(logging.INFO)
    
    # Set formatter
    if formatter:
        file_handler.setFormatter(formatter)
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
    
    # Add to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Added file handler: {file_path}")
    
    return file_handler


def remove_handler(handler: logging.Handler) -> None:
    """
    Remove a specific handler from the root logger.
    
    Args:
        handler (logging.Handler): Handler to remove
    """
    root_logger = logging.getLogger()
    if handler in root_logger.handlers:
        root_logger.removeHandler(handler)
        handler.close()
        
        logger = logging.getLogger(__name__)
        logger.info("Handler removed successfully")


class StructuredLogger:
    """
    Structured logger that provides consistent logging across the application.
    
    This class provides methods for logging different types of events
    with consistent structure and formatting.
    """
    
    def __init__(self, name: str):
        """
        Initialize the structured logger.
        
        Args:
            name (str): Logger name
        """
        self.logger = logging.getLogger(name)
    
    def log_news_collection(self, source: str, count: int, duration: float):
        """
        Log news collection results.
        
        Args:
            source (str): Name of the news source
            count (int): Number of news items collected
            duration (float): Time taken for collection in seconds
        """
        self.logger.info(
            f"News collection completed",
            extra={
                'source': source,
                'count': count,
                'duration_seconds': duration,
                'event_type': 'news_collection'
            }
        )
    
    def log_processing_step(self, step: str, input_count: int, output_count: int, duration: float):
        """
        Log processing step results.
        
        Args:
            step (str): Name of the processing step
            input_count (int): Number of input items
            output_count (int): Number of output items
            duration (float): Time taken for processing in seconds
        """
        self.logger.info(
            f"Processing step completed",
            extra={
                'step': step,
                'input_count': input_count,
                'output_count': output_count,
                'duration_seconds': duration,
                'event_type': 'processing_step'
            }
        )
    
    def log_error(self, error: str, context: dict = None):
        """
        Log an error with context.
        
        Args:
            error (str): Error description
            context (dict, optional): Additional context information
        """
        extra = {'event_type': 'error'}
        if context:
            extra.update(context)
        
        self.logger.error(error, extra=extra)
    
    def log_warning(self, warning: str, context: dict = None):
        """
        Log a warning with context.
        
        Args:
            warning (str): Warning description
            context (dict, optional): Additional context information
        """
        extra = {'event_type': 'warning'}
        if context:
            extra.update(context)
        
        self.logger.warning(warning, extra=extra) 