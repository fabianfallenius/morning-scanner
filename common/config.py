"""
Configuration management for the Morning Scanner application.

This module handles all configuration settings including:
- Environment variables
- Default values
- Configuration validation using Pydantic
- Type safety and helpful error messages
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Config(BaseSettings):
    """
    Configuration class that manages all application settings.
    
    This class uses Pydantic BaseSettings to:
    - Automatically load from .env files
    - Validate types and provide helpful error messages
    - Set sensible defaults
    - Ensure configuration integrity
    """
    
    # Timezone and scheduling settings
    TZ: str = Field(default="Europe/Stockholm", description="Application timezone")
    RUN_HOUR: int = Field(default=8, ge=0, le=23, description="Hour to run scanner (0-23)")
    RUN_MINUTE: int = Field(default=40, ge=0, le=59, description="Minute to run scanner (0-59)")
    
    # Email configuration
    EMAIL_ENABLED: bool = Field(default=False, description="Enable email notifications")
    SMTP_HOST: str = Field(default="smtp.gmail.com", description="SMTP server hostname")
    SMTP_PORT: int = Field(default=587, ge=1, le=65535, description="SMTP server port")
    SMTP_USER: str = Field(default="", description="SMTP username/email")
    SMTP_PASS: str = Field(default="", description="SMTP password/app password")
    EMAIL_TO: str = Field(default="", description="Recipient email address")
    
    # Telegram configuration
    TELEGRAM_ENABLED: bool = Field(default=False, description="Enable Telegram notifications")
    TELEGRAM_BOT_TOKEN: str = Field(default="", description="Telegram bot token")
    TELEGRAM_CHAT_ID: str = Field(default="", description="Telegram chat ID")
    
    # AI/LLM configuration
    USE_LLM: bool = Field(default=False, description="Enable LLM-based analysis")
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key (optional)")
    
    # News source settings
    MFN_BASE_URL: str = Field(default="https://www.mfn.se", description="MFN base URL")
    MFN_DELAY: int = Field(default=2, ge=0, description="Delay between MFN requests (seconds)")
    DI_MORGONKOLL_BASE_URL: str = Field(default="https://www.di.se", description="DI Morgonkoll base URL")
    DI_MORGONKOLL_DELAY: int = Field(default=3, ge=0, description="Delay between DI requests (seconds)")
    
    # Scraping settings
    RESPECT_ROBOTS_TXT: bool = Field(default=True, description="Respect robots.txt files")
    USER_AGENT: str = Field(
        default="Mozilla/5.0 (compatible; MorningScanner/1.0; +https://github.com/yourusername/morning-scanner)",
        description="User agent for web requests"
    )
    REQUEST_TIMEOUT: int = Field(default=30, ge=1, description="Request timeout in seconds")
    
    # Ranking and filtering
    MIN_RELEVANCE_SCORE: float = Field(default=0.3, ge=0.0, le=1.0, description="Minimum relevance score (0.0-1.0)")
    MAX_ITEMS_PER_REPORT: int = Field(default=20, ge=1, description="Maximum items per report")
    
    # Storage settings
    PICKS_LOG_FILE: str = Field(default="storage/picks_log.csv", description="Picks log file path")
    ERROR_LOG_FILE: str = Field(default="storage/errors.log", description="Error log file path")
    
    # Development settings
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    DRY_RUN: bool = Field(default=False, description="Enable dry run mode (no actual scraping)")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_prefix = ""  # No prefix for environment variables
    
    @validator('EMAIL_ENABLED', 'TELEGRAM_ENABLED')
    def validate_notification_config(cls, v, values):
        """Validate notification configuration when enabled."""
        if v:  # If notification is enabled
            if 'EMAIL_ENABLED' in values and values['EMAIL_ENABLED']:
                # Validate email settings
                if not values.get('SMTP_USER') or not values.get('SMTP_PASS') or not values.get('EMAIL_TO'):
                    raise ValueError(
                        "Email is enabled but missing required settings: "
                        "SMTP_USER, SMTP_PASS, or EMAIL_TO"
                    )
            
            if 'TELEGRAM_ENABLED' in values and values['TELEGRAM_ENABLED']:
                # Validate Telegram settings
                if not values.get('TELEGRAM_BOT_TOKEN') or not values.get('TELEGRAM_CHAT_ID'):
                    raise ValueError(
                        "Telegram is enabled but missing required settings: "
                        "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID"
                    )
        
        return v
    
    @validator('OPENAI_API_KEY')
    def validate_openai_key(cls, v, values):
        """Validate OpenAI API key when LLM is enabled."""
        if values.get('USE_LLM') and not v:
            raise ValueError("USE_LLM is enabled but OPENAI_API_KEY is not provided")
        return v
    
    @validator('TZ')
    def validate_timezone(cls, v):
        """Validate timezone string."""
        try:
            import pytz
            pytz.timezone(v)
            return v
        except Exception:
            raise ValueError(f"Invalid timezone: {v}. Use format like 'Europe/Stockholm'")
    
    def get_scraping_delay(self, source_name: str) -> int:
        """
        Get the appropriate delay for a specific news source.
        
        Args:
            source_name (str): Name of the news source
            
        Returns:
            int: Delay in seconds for the source
        """
        delays = {
            'mfn': self.MFN_DELAY,
            'di_morgonkoll': self.DI_MORGONKOLL_DELAY,
            'extras': 1  # Default delay for extra sources
        }
        
        return delays.get(source_name.lower(), 1)
    
    def is_development_mode(self) -> bool:
        """
        Check if the application is running in development mode.
        
        Returns:
            bool: True if in development mode
        """
        return self.DEBUG or self.DRY_RUN
    
    def get_schedule_time(self) -> tuple[int, int]:
        """
        Get the scheduled run time as (hour, minute).
        
        Returns:
            tuple[int, int]: Hour and minute for scheduled runs
        """
        return (self.RUN_HOUR, self.RUN_MINUTE)
    
    def __repr__(self) -> str:
        """String representation of the configuration."""
        return (f"Config(timezone='{self.TZ}', "
                f"schedule='{self.RUN_HOUR:02d}:{self.RUN_MINUTE:02d}', "
                f"email_enabled={self.EMAIL_ENABLED}, "
                f"telegram_enabled={self.TELEGRAM_ENABLED}, "
                f"use_llm={self.USE_LLM})")


# Global configuration instance
config = Config()


def get_config() -> Config:
    """
    Get the global configuration instance.
    
    Returns:
        Config: Global configuration object
    """
    return config


def reload_config() -> Config:
    """
    Reload configuration from environment variables.
    
    Returns:
        Config: Reloaded configuration object
    """
    global config
    config = Config()
    return config 