"""
Email sender for Morning Scanner reports.

This module provides:
- Daily news report emails
- Positive stock article summaries
- HTML and text email formats
- Configurable email templates
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional
from datetime import datetime

from common.config import get_config
from common.utils_time import now_se


class EmailSender:
    """
    Send email reports for the Morning Scanner.
    
    This class provides:
    - Daily news summaries
    - Positive stock recommendations
    - Configurable email templates
    - HTML and text formatting
    """
    
    def __init__(self):
        """Initialize the email sender."""
        self.logger = logging.getLogger(__name__)
        self.config = get_config()
        
        # For testing purposes, don't validate config immediately
        # This allows the system to work even without email configuration
        self._config_valid = None
        
        self.logger.info("Email sender initialized")
    
    def _validate_config(self) -> bool:
        """Validate email configuration."""
        # Cache validation result
        if self._config_valid is not None:
            return self._config_valid
        
        required_fields = ['SMTP_HOST', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASS', 'EMAIL_TO']
        
        for field in required_fields:
            if not getattr(self.config, field, None):
                self.logger.error(f"Missing required email configuration: {field}")
                self._config_valid = False
                return False
        
        self._config_valid = True
        return True
    
    def is_configured(self) -> bool:
        """Check if email is properly configured."""
        return self._validate_config()
    
    def send_daily_report(self, news_items: List[Dict], insights: Dict) -> bool:
        """
        Send daily news report email.
        
        Args:
            news_items (List[Dict]): List of classified news items
            insights (Dict): News analysis insights
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Check if email is configured
            if not self.is_configured():
                self.logger.warning("Email not configured - cannot send daily report")
                return False
            
            # Filter for positive and high-impact news
            positive_news = self._filter_positive_news(news_items)
            
            # Create email content
            subject = self._create_subject(insights)
            html_content = self._create_html_report(positive_news, insights)
            text_content = self._create_text_report(positive_news, insights)
            
            # Send email
            success = self._send_email(subject, html_content, text_content)
            
            if success:
                self.logger.info(f"Daily report email sent successfully to {self.config.EMAIL_TO}")
            else:
                self.logger.error("Failed to send daily report email")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending daily report: {str(e)}")
            return False
    
    def send_alert(self, title: str, message: str, priority: str = 'normal') -> bool:
        """
        Send an alert email.
        
        Args:
            title (str): Alert title
            message (str): Alert message
            priority (str): Priority level ('low', 'normal', 'high')
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Check if email is configured
            if not self.is_configured():
                self.logger.warning("Email not configured - cannot send alert")
                return False
            
            subject = f"[{priority.upper()}] {title}"
            html_content = self._create_alert_html(title, message, priority)
            text_content = self._create_alert_text(title, message, priority)
            
            success = self._send_email(subject, html_content, text_content)
            
            if success:
                self.logger.info(f"Alert email sent successfully: {title}")
            else:
                self.logger.error(f"Failed to send alert email: {title}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending alert: {str(e)}")
            return False
    
    def _filter_positive_news(self, news_items: List[Dict]) -> List[Dict]:
        """
        Filter news items for positive content.
        
        Args:
            news_items (List[Dict]): All news items
            
        Returns:
            List[Dict]: Filtered positive news items
        """
        positive_news = []
        
        for item in news_items:
            classification = item.get('classification', {})
            
            # Include if:
            # 1. High relevance score
            # 2. Positive sentiment
            # 3. High impact
            # 4. Contains catalyst events
            
            # Handle both dictionary and object access
            if hasattr(classification, 'relevance_score'):
                # It's a NewsClassification object
                relevance_score = classification.relevance_score
                sentiment_score = classification.sentiment_score
                impact_level = classification.impact_level
                has_catalyst = classification.has_catalyst
            else:
                # It's a dictionary (fallback)
                relevance_score = classification.get('relevance_score', 0)
                sentiment_score = classification.get('sentiment_score', 0)
                impact_level = classification.get('impact_level', 'low')
                has_catalyst = classification.get('has_catalyst', False)
            
            if (relevance_score >= 0.4 and  # Medium to high relevance
                (sentiment_score > 0.1 or  # Positive sentiment
                 has_catalyst or           # Catalyst event
                 impact_level == 'high')): # High impact
                
                positive_news.append(item)
        
        # Sort by relevance score (highest first)
        positive_news.sort(key=lambda x: getattr(x.get('classification', {}), 'relevance_score', 0) if hasattr(x.get('classification', {}), 'relevance_score') else x.get('classification', {}).get('relevance_score', 0), reverse=True)
        
        # Limit to top 15 items
        return positive_news[:15]
    
    def _create_subject(self, insights: Dict) -> str:
        """Create email subject line."""
        date_str = now_se().strftime('%Y-%m-%d')
        catalyst_count = insights.get('catalyst_events', 0)
        high_impact = insights.get('impact_distribution', {}).get('high', 0)
        
        if catalyst_count > 0:
            return f"🚀 Morning Scanner {date_str} - {catalyst_count} Catalyst Events!"
        elif high_impact > 0:
            return f"📈 Morning Scanner {date_str} - {high_impact} High-Impact News"
        else:
            return f"📰 Morning Scanner {date_str} - Daily News Summary"
    
    def _create_html_report(self, positive_news: List[Dict], insights: Dict) -> str:
        """Create HTML email content."""
        date_str = now_se().strftime('%Y-%m-%d %H:%M')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
                .summary {{ background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .news-item {{ background: white; border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .news-title {{ color: #2c3e50; font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
                .news-snippet {{ color: #555; margin-bottom: 15px; }}
                .news-meta {{ color: #888; font-size: 14px; }}
                .news-url {{ background: #007bff; color: white; padding: 8px 12px; border-radius: 6px; text-decoration: none; display: inline-block; margin: 10px 0; font-weight: bold; }}
                .news-url:hover {{ background: #0056b3; }}
                .positive-badge {{ background: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; margin-left: 10px; }}
                .catalyst-badge {{ background: #ffc107; color: #212529; padding: 4px 8px; border-radius: 4px; font-size: 12px; margin-left: 10px; }}
                .high-impact-badge {{ background: #dc3545; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; margin-left: 10px; }}
                .footer {{ text-align: center; color: #888; margin-top: 30px; padding: 20px; border-top: 1px solid #e9ecef; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌅 Morning Scanner</h1>
                <p>Swedish Financial News Analysis - {date_str}</p>
            </div>
            
            <div class="summary">
                <h2>📊 Market Summary</h2>
                <p><strong>Total News Items:</strong> {insights.get('total_items', 0)}</p>
                <p><strong>High Impact News:</strong> {insights.get('impact_distribution', {}).get('high', 0)}</p>
                <p><strong>Catalyst Events:</strong> {insights.get('catalyst_events', 0)}</p>
                <p><strong>Market Sentiment:</strong> {insights.get('insights', 'Standard market activity')}</p>
            </div>
            
            <h2>🚀 Positive Stock Opportunities</h2>
        """
        
        if positive_news:
            for item in positive_news:
                classification = item.get('classification', {})
                title = item.get('title', 'No title')
                snippet = item.get('snippet', 'No snippet')
                url = item.get('url', '#')
                source = item.get('source', 'Unknown')
                timestamp = item.get('timestamp', 'Unknown time')
                
                # Create badges
                badges = []
                if hasattr(classification, 'sentiment_score') and classification.sentiment_score > 0.1:
                    badges.append('<span class="positive-badge">POSITIVE</span>')
                if hasattr(classification, 'has_catalyst') and classification.has_catalyst:
                    badges.append('<span class="catalyst-badge">⚡ CATALYST</span>')
                if hasattr(classification, 'impact_level') and classification.impact_level == 'high':
                    badges.append('<span class="high-impact-badge">HIGH IMPACT</span>')
                
                badges_html = ' '.join(badges)
                
                html += f"""
                <div class="news-item">
                    <div class="news-title">
                        <a href="{url}" style="color: #2c3e50; text-decoration: none;">{title}</a>
                        {badges_html}
                    </div>
                    <div class="news-snippet">{snippet}</div>
                    <div class="news-meta">
                        <strong>Why this is good:</strong> {self._explain_why_good(classification)}<br>
                        <strong>Source:</strong> {source} | <strong>Time:</strong> {timestamp}
                    </div>
                    <div style="margin-top: 15px;">
                        <a href="{url}" class="news-url" target="_blank">📖 READ FULL ARTICLE</a>
                    </div>
                </div>
                """
        else:
            html += """
            <div class="news-item">
                <p>No significant positive news detected today. Market may be quiet or sentiment is neutral.</p>
            </div>
            """
        
        html += f"""
            <div class="footer">
                <p>Generated by Morning Scanner at {date_str}</p>
                <p>This is an automated report. Please verify information before making investment decisions.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_text_report(self, positive_news: List[Dict], insights: Dict) -> str:
        """Create plain text email content."""
        date_str = now_se().strftime('%Y-%m-%d %H:%M')
        
        text = f"""
MORNING SCANNER - Swedish Financial News Analysis
{date_str}
{'=' * 60}

MARKET SUMMARY:
- Total News Items: {insights.get('total_items', 0)}
- High Impact News: {insights.get('impact_distribution', {}).get('high', 0)}
- Catalyst Events: {insights.get('catalyst_events', 0)}
- Market Sentiment: {insights.get('insights', 'Standard market activity')}

POSITIVE STOCK OPPORTUNITIES:
{'=' * 60}

"""
        
        if positive_news:
            for i, item in enumerate(positive_news, 1):
                classification = item.get('classification', {})
                title = item.get('title', 'No title')
                snippet = item.get('snippet', 'No snippet')
                url = item.get('url', '#')
                source = item.get('source', 'Unknown')
                timestamp = item.get('timestamp', 'Unknown time')
                
                # Create badges
                badges = []
                if hasattr(classification, 'sentiment_score') and classification.sentiment_score > 0.1:
                    badges.append('[POSITIVE]')
                if hasattr(classification, 'has_catalyst') and classification.has_catalyst:
                    badges.append('[⚡ CATALYST]')
                if hasattr(classification, 'impact_level') and classification.impact_level == 'high':
                    badges.append('[HIGH IMPACT]')
                
                badges_text = ' '.join(badges)
                
                text += f"""
{i}. {title} {badges_text}

   {snippet}

   Why this is good: {self._explain_why_good(classification)}
   Source: {source} | Time: {timestamp}
   
   🔗 READ FULL ARTICLE: {url}

{'-' * 60}
"""
        else:
            text += """
No significant positive news detected today. Market may be quiet or sentiment is neutral.

"""
        
        text += f"""
{'=' * 60}
Generated by Morning Scanner at {date_str}
This is an automated report. Please verify information before making investment decisions.
"""
        
        return text
    
    def _explain_why_good(self, classification: Dict) -> str:
        """Explain why a news item is considered positive."""
        reasons = []
        
        # Handle both dictionary and object access
        if hasattr(classification, 'sentiment_score'):
            # It's a NewsClassification object
            sentiment_score = classification.sentiment_score
            impact_level = classification.impact_level
            has_catalyst = classification.has_catalyst
            categories = classification.categories
        else:
            # It's a dictionary (fallback)
            sentiment_score = classification.get('sentiment_score', 0)
            impact_level = classification.get('impact_level', 'low')
            has_catalyst = classification.get('has_catalyst', False)
            categories = classification.get('categories', [])
        
        if sentiment_score > 0.3:
            reasons.append("Strong positive sentiment")
        elif sentiment_score > 0.1:
            reasons.append("Positive sentiment")
        
        if impact_level == 'high':
            reasons.append("High market impact")
        elif impact_level == 'medium':
            reasons.append("Moderate market impact")
        
        if has_catalyst:
            reasons.append("Catalyst event detected")
        
        if categories:
            category_names = {
                'earnings': 'Earnings related',
                'orders': 'Order/contract related',
                'guidance': 'Guidance/prognosis related',
                'regulatory': 'Regulatory approval',
                'corporate': 'Corporate action',
                'financial': 'Financial development',
                'market': 'Market activity',
                'industry': 'Industry development'
            }
            
            for category in categories:
                if category in category_names:
                    reasons.append(category_names[category])
        
        if not reasons:
            reasons.append("Relevant financial news")
        
        return "; ".join(reasons)
    
    def _create_alert_html(self, title: str, message: str, priority: str) -> str:
        """Create HTML alert email."""
        priority_colors = {
            'low': '#17a2b8',
            'normal': '#ffc107',
            'high': '#dc3545'
        }
        
        color = priority_colors.get(priority, '#6c757d')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .alert {{ background: {color}; color: white; padding: 20px; border-radius: 8px; }}
                .content {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; border: 1px solid #e9ecef; }}
            </style>
        </head>
        <body>
            <div class="alert">
                <h2>🚨 {title}</h2>
                <p>Priority: {priority.upper()}</p>
            </div>
            
            <div class="content">
                <p>{message}</p>
            </div>
            
            <p style="color: #888; text-align: center;">
                Generated by Morning Scanner at {now_se().strftime('%Y-%m-%d %H:%M')}
            </p>
        </body>
        </html>
        """
        
        return html
    
    def _create_alert_text(self, title: str, message: str, priority: str) -> str:
        """Create plain text alert email."""
        text = f"""
🚨 ALERT: {title}
Priority: {priority.upper()}
{'=' * 60}

{message}

{'=' * 60}
Generated by Morning Scanner at {now_se().strftime('%Y-%m-%d %H:%M')}
"""
        
        return text
    
    def _send_email(self, subject: str, html_content: str, text_content: str) -> bool:
        """
        Send email with both HTML and text content.
        
        Args:
            subject (str): Email subject
            html_content (str): HTML email content
            text_content (str): Plain text email content
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config.SMTP_USER
            msg['To'] = self.config.EMAIL_TO
            
            # Add text and HTML parts
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.config.SMTP_HOST, self.config.SMTP_PORT) as server:
                server.starttls()
                server.login(self.config.SMTP_USER, self.config.SMTP_PASS)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False


# Global instance for easy access
email_sender = EmailSender()


def get_email_sender() -> EmailSender:
    """
    Get the global email sender instance.
    
    Returns:
        EmailSender: Email sender instance
    """
    return email_sender 