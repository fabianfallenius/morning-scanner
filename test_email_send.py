#!/usr/bin/env python3
"""Test script to send an actual email with sample data."""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_send_email():
    """Send a test email with sample positive stock opportunities."""
    try:
        from output.sender_email import get_email_sender
        from nlp.classify import get_news_classifier
        
        print("📧 Testing Email Sending with Sample Data")
        print("=" * 60)
        
        # Get components
        email_sender = get_email_sender()
        news_classifier = get_news_classifier()
        
        # Check if email is configured
        if not email_sender.is_configured():
            print("❌ Email not configured properly. Please check your .env file.")
            print("Required fields: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_TO")
            return False
        
        print(f"✅ Email configuration valid")
        print(f"From: {email_sender.config.SMTP_USER}")
        print(f"To: {email_sender.config.EMAIL_TO}")
        
        # Create sample positive news data
        sample_news = [
            {
                'title': 'Ericsson överträffar förväntningarna med stark rapport Q3',
                'snippet': 'Telekomjätten redovisar bättre resultat än väntat med stark orderingång från 5G-segment. Höjer prognos för helåret.',
                'url': 'https://example.com/ericsson-q3-strong',
                'source': 'MFN',
                'timestamp': '2025-08-22T08:30:00'
            },
            {
                'title': 'Volvo Cars vinner miljardorder från europeisk biluthyrare',
                'snippet': 'Strategiskt ramavtal värt 3,5 miljarder kronor över tre år. Fokus på elektriska fordon stärker framtidsutsikter.',
                'url': 'https://example.com/volvo-big-contract',
                'source': 'DI Morgonkoll',
                'timestamp': '2025-08-22T08:15:00'
            },
            {
                'title': 'AstraZeneca får FDA-godkännande för cancermedicin',
                'snippet': 'Regulatoriskt genombrott öppnar för global kommersialisering av ny onkologibehandling. Royaltyintäkter väntas.',
                'url': 'https://example.com/astrazeneca-fda',
                'source': 'MFN',
                'timestamp': '2025-08-22T07:45:00'
            },
            {
                'title': 'Atlas Copco lanserar revolutionerande kompressorteknik',
                'snippet': 'Produktlansering med 40% högre energieffektivitet. Patent beviljat för ny kompressorteknik.',
                'url': 'https://example.com/atlas-copco-innovation',
                'source': 'DI Morgonkoll',
                'timestamp': '2025-08-22T07:30:00'
            },
            {
                'title': 'SEB höjer riktkurs för svenska industribolag',
                'snippet': 'Banken uppgraderar flera svenska industriaktier till köpråd. Stark köprekommendation för sektorn.',
                'url': 'https://example.com/seb-upgrades',
                'source': 'MFN',
                'timestamp': '2025-08-22T07:00:00'
            }
        ]
        
        print(f"\n🔍 Analyzing {len(sample_news)} sample news items...")
        
        # Classify the sample news
        classified_news = []
        for item in sample_news:
            classification = news_classifier.classify_news(
                item['title'], 
                '',  # No full content
                item['snippet']
            )
            item['classification'] = classification
            classified_news.append(item)
        
        # Generate insights
        insights = news_classifier.get_news_insights(classified_news)
        
        print(f"📊 Market Insights Generated:")
        print(f"   - Total Items: {insights['total_items']}")
        print(f"   - High Impact: {insights['impact_distribution']['high']}")
        print(f"   - Catalyst Events: {insights['catalyst_events']}")
        print(f"   - Market Sentiment: {insights['insights']}")
        
        # Send the email
        print(f"\n📧 Sending test email...")
        
        success = email_sender.send_daily_report(classified_news, insights)
        
        if success:
            print(f"🎉 Test email sent successfully!")
            print(f"📬 Check your inbox at: {email_sender.config.EMAIL_TO}")
            print(f"")
            print(f"The email contains:")
            print(f"   📈 {len([item for item in classified_news if item['classification'].relevance_score >= 0.4])} positive stock opportunities")
            print(f"   ⚡ {insights['catalyst_events']} catalyst events")
            print(f"   🎯 Relevance-ranked articles with explanations")
            print(f"   📊 Market summary and insights")
            return True
        else:
            print(f"❌ Failed to send test email")
            print(f"Check your email configuration and try again.")
            return False
    
    except Exception as e:
        print(f"❌ Error sending test email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def send_test_alert():
    """Send a simple test alert email."""
    try:
        from output.sender_email import get_email_sender
        
        print(f"\n📨 Sending Simple Test Alert...")
        
        email_sender = get_email_sender()
        
        if not email_sender.is_configured():
            print("❌ Email not configured")
            return False
        
        success = email_sender.send_alert(
            title="Morning Scanner Test Alert",
            message="This is a test message from your Morning Scanner. If you're reading this, your email configuration is working correctly!",
            priority="normal"
        )
        
        if success:
            print(f"✅ Test alert sent successfully!")
            return True
        else:
            print(f"❌ Failed to send test alert")
            return False
    
    except Exception as e:
        print(f"❌ Error sending test alert: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Morning Scanner Email Test")
    print("=" * 60)
    
    # Test 1: Send sample daily report
    print("Test 1: Sending sample daily report with positive stock opportunities...")
    test1_success = test_send_email()
    
    # Test 2: Send simple alert
    print("\nTest 2: Sending simple test alert...")
    test2_success = send_test_alert()
    
    print(f"\n{'=' * 60}")
    print(f"Test Results:")
    print(f"   Daily Report: {'✅ Success' if test1_success else '❌ Failed'}")
    print(f"   Simple Alert: {'✅ Success' if test2_success else '❌ Failed'}")
    
    if test1_success and test2_success:
        print(f"\n🎉 All email tests passed!")
        print(f"📬 Check your inbox for the test emails.")
        print(f"🚀 Your Morning Scanner is ready for daily use!")
        sys.exit(0)
    else:
        print(f"\n❌ Some email tests failed.")
        print(f"💡 Check your .env configuration and try again.")
        sys.exit(1) 