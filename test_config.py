#!/usr/bin/env python3
"""Test script to verify configuration loading."""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config():
    """Test configuration loading."""
    try:
        from common.config import get_config
        config = get_config()
        
        print("✓ Configuration loaded successfully!")
        print(f"Timezone: {config.TZ}")
        print(f"Schedule: {config.RUN_HOUR:02d}:{config.RUN_MINUTE:02d}")
        print(f"Email enabled: {config.EMAIL_ENABLED}")
        print(f"Telegram enabled: {config.TELEGRAM_ENABLED}")
        print(f"Use LLM: {config.USE_LLM}")
        print(f"MFN Base URL: {config.MFN_BASE_URL}")
        print(f"DI Morgonkoll Base URL: {config.DI_MORGONKOLL_BASE_URL}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {str(e)}")
        return False

def test_time_utils():
    """Test time utilities."""
    try:
        from common.utils_time import now_se, today_date_se, is_trading_day_sweden
        
        print("\n✓ Time utilities test:")
        print(f"Current time (SE): {now_se()}")
        print(f"Today's date (SE): {today_date_se()}")
        print(f"Is trading day: {is_trading_day_sweden()}")
        
        return True
        
    except Exception as e:
        print(f"✗ Time utilities test failed: {str(e)}")
        return False

def test_logging():
    """Test logging setup."""
    try:
        from common.logging_setup import setup_logging, get_logger
        
        print("\n✓ Logging test:")
        setup_logging()
        logger = get_logger(__name__)
        logger.info("Test log message")
        print("Logging setup successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Logging test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Morning Scanner Configuration...")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config),
        ("Time Utilities", test_time_utils),
        ("Logging", test_logging)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- Testing {test_name} ---")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print(f"\n{'=' * 50}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Configuration is working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the configuration.")
        sys.exit(1) 