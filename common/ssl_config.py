#!/usr/bin/env python3
"""SSL Configuration for Morning Scanner - Handles certificate verification and SSL contexts."""

import ssl
import certifi
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class SSLConfig:
    """Manages SSL configurations for different scenarios."""
    
    def __init__(self):
        self.certifi_path = certifi.where()
        self.default_context = None
        self.relaxed_context = None
        self._setup_contexts()
    
    def _setup_contexts(self):
        """Setup different SSL contexts."""
        try:
            # Default strict context
            self.default_context = ssl.create_default_context(
                cafile=self.certifi_path
            )
            self.default_context.verify_mode = ssl.CERT_REQUIRED
            self.default_context.check_hostname = True
            
            # Relaxed context for problematic sites
            self.relaxed_context = ssl.create_default_context(
                cafile=self.certifi_path
            )
            self.relaxed_context.verify_mode = ssl.CERT_REQUIRED
            self.relaxed_context.check_hostname = False  # More permissive
            
            logger.info(f"SSL contexts configured using certifi: {self.certifi_path}")
            
        except Exception as e:
            logger.error(f"Failed to setup SSL contexts: {e}")
            # Fallback to system defaults
            self.default_context = ssl.create_default_context()
            self.relaxed_context = ssl.create_default_context()
    
    def get_context(self, strict: bool = True) -> ssl.SSLContext:
        """
        Get SSL context based on strictness requirement.
        
        Args:
            strict: If True, use strict verification. If False, use relaxed.
            
        Returns:
            SSL context configured appropriately
        """
        if strict:
            return self.default_context
        else:
            return self.relaxed_context
    
    def get_aiohttp_ssl_context(self, strict: bool = True) -> ssl.SSLContext:
        """
        Get SSL context specifically for aiohttp.
        
        Args:
            strict: If True, use strict verification. If False, use relaxed.
            
        Returns:
            SSL context for aiohttp
        """
        context = self.get_context(strict)
        
        # aiohttp specific optimizations
        context.options |= ssl.OP_NO_COMPRESSION
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # Force TLS 1.2+
        
        return context
    
    def get_requests_ssl_context(self, strict: bool = True) -> ssl.SSLContext:
        """
        Get SSL context specifically for requests library.
        
        Args:
            strict: If True, use strict verification. If False, use relaxed.
            
        Returns:
            SSL context for requests
        """
        return self.get_context(strict)
    
    def test_connection(self, url: str, strict: bool = True) -> Dict[str, Any]:
        """
        Test SSL connection to a URL.
        
        Args:
            url: URL to test
            strict: Whether to use strict SSL verification
            
        Returns:
            Dictionary with connection test results
        """
        import urllib.request
        
        try:
            context = self.get_context(strict)
            req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, context=context) as response:
                return {
                    'success': True,
                    'status': response.status,
                    'strict': strict,
                    'url': url
                }
                
        except ssl.SSLCertVerificationError as e:
            return {
                'success': False,
                'error': 'SSL_CERT_VERIFICATION_FAILED',
                'message': str(e),
                'strict': strict,
                'url': url
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'CONNECTION_FAILED',
                'message': str(e),
                'strict': strict,
                'url': url
            }
    
    def get_ssl_info(self) -> Dict[str, Any]:
        """Get comprehensive SSL configuration information."""
        return {
            'certifi_path': self.certifi_path,
            'openssl_version': ssl.OPENSSL_VERSION,
            'default_verify_paths': str(ssl.get_default_verify_paths()),
            'has_default_context': self.default_context is not None,
            'has_relaxed_context': self.relaxed_context is not None
        }


# Global SSL configuration instance
ssl_config = SSLConfig()


def get_ssl_config() -> SSLConfig:
    """Get the global SSL configuration instance."""
    return ssl_config


def test_news_sources_ssl():
    """Test SSL connections to all news sources."""
    news_sources = [
        'https://www.mfn.se',
        'https://www.di.se',
        'https://www.svt.se',
        'https://sverigesradio.se'
    ]
    
    print("🔐 Testing SSL Connections to News Sources")
    print("=" * 60)
    
    for url in news_sources:
        print(f"\n🔍 Testing: {url}")
        
        # Test strict first
        strict_result = ssl_config.test_connection(url, strict=True)
        if strict_result['success']:
            print(f"   ✅ Strict SSL: SUCCESS")
        else:
            print(f"   ❌ Strict SSL: FAILED - {strict_result['error']}")
            
            # Test relaxed if strict failed
            relaxed_result = ssl_config.test_connection(url, strict=False)
            if relaxed_result['success']:
                print(f"   ⚠️  Relaxed SSL: SUCCESS (use this for production)")
            else:
                print(f"   ❌ Relaxed SSL: FAILED - {relaxed_result['error']}")
    
    print(f"\n📊 SSL Configuration Info:")
    ssl_info = ssl_config.get_ssl_info()
    for key, value in ssl_info.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    # Setup basic logging
    logging.basicConfig(level=logging.INFO)
    
    # Test SSL connections
    test_news_sources_ssl() 