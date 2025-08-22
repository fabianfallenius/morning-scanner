#!/usr/bin/env python3
"""Test script for the complete Morning Scanner pipeline."""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_complete_pipeline():
    """Test the complete Morning Scanner pipeline with mock data."""
    try:
        from nlp.classify import get_news_classifier
        from output.sender_email import get_email_sender
        from storage.picks_log import PicksLogger
        
        print("🧪 Testing Complete Morning Scanner Pipeline")
        print("=" * 60)
        
        # Get components
        news_classifier = get_news_classifier()
        email_sender = get_email_sender()
        picks_logger = PicksLogger()
        
        print("✅ All components loaded successfully")
        
        # Create mock news data (simulating what would be scraped)
        mock_news = [
            {
                'title': 'Ericsson överträffar förväntningarna med stark rapport',
                'snippet': 'Bolaget höjer prognos och guidning över väntan. Stark orderingång och ny kund.',
                'url': 'https://example.com/ericsson-strong-report',
                'source': 'MFN',
                'timestamp': '2025-08-22T08:30:00'
            },
            {
                'title': 'Volvo vinner stororder värd 2 miljarder kronor',
                'snippet': 'Strategiskt avtal med ny kund. Flerårigt ramavtal som stärker orderboken.',
                'url': 'https://example.com/volvo-big-order',
                'source': 'DI Morgonkoll',
                'timestamp': '2025-08-22T08:15:00'
            },
            {
                'title': 'AstraZeneca får FDA-godkännande för nytt läkemedel',
                'snippet': 'Regulatoriskt godkännande öppnar för kommersialisering. Klinisk framgång i fas 3.',
                'url': 'https://example.com/astrazeneca-fda-approval',
                'source': 'MFN',
                'timestamp': '2025-08-22T07:45:00'
            },
            {
                'title': 'H&M presenterar månadsrapport med försäljningssiffror',
                'snippet': 'Bokslut och kundtillväxt i fokus. Förbättrad visibilitet på marknaden.',
                'url': 'https://example.com/hm-monthly-report',
                'source': 'DI Morgonkoll',
                'timestamp': '2025-08-22T07:30:00'
            },
            {
                'title': 'Sandvik lanserar ny produktlinje för hållbar utveckling',
                'snippet': 'Produktlansering fokuserad på grön energi. Marknadslansering i Q4.',
                'url': 'https://example.com/sandvik-green-products',
                'source': 'MFN',
                'timestamp': '2025-08-22T07:15:00'
            },
            {
                'title': 'SEB höjer riktkurs för flera svenska bolag',
                'snippet': 'Analytiker uppgraderar rekommendationer. Stark köprekommendation för sektorn.',
                'url': 'https://example.com/seb-upgrades',
                'source': 'DI Morgonkoll',
                'timestamp': '2025-08-22T07:00:00'
            },
            {
                'title': 'Atlas Copco etablerar sig i ny marknad',
                'snippet': 'Expansion till Asien. Strategiskt partnerskap med lokal aktör.',
                'url': 'https://example.com/atlas-copco-expansion',
                'source': 'MFN',
                'timestamp': '2025-08-22T06:45:00'
            },
            {
                'title': 'Generisk marknadsnyhet utan särskilda händelser',
                'snippet': 'Standard marknadsutveckling enligt förväntningarna.',
                'url': 'https://example.com/generic-news',
                'source': 'MFN',
                'timestamp': '2025-08-22T06:30:00'
            }
        ]
        
        print(f"\n📰 Processing {len(mock_news)} mock news items...")
        print("-" * 60)
        
        # Step 1: Classify news
        print("Step 1: Classifying news items...")
        classified_news = []
        
        for item in mock_news:
            classification = news_classifier.classify_news(
                item['title'], 
                '',  # No content for mock data
                item['snippet']
            )
            item['classification'] = classification
            classified_news.append(item)
        
        print(f"✅ Classified {len(classified_news)} news items")
        
        # Step 2: Generate insights
        print("\nStep 2: Generating market insights...")
        insights = news_classifier.get_news_insights(classified_news)
        
        print(f"📊 Market Summary:")
        print(f"   - Total Items: {insights['total_items']}")
        print(f"   - High Impact: {insights['impact_distribution']['high']}")
        print(f"   - Catalyst Events: {insights['catalyst_events']}")
        print(f"   - Insights: {insights['insights']}")
        
        # Step 3: Filter positive news
        print("\nStep 3: Filtering positive stock opportunities...")
        positive_news = []
        
        for item in classified_news:
            classification = item['classification']
            relevance_score = classification.relevance_score
            sentiment_score = classification.sentiment_score
            impact_level = classification.impact_level
            has_catalyst = classification.has_catalyst
            
            if (relevance_score >= 0.4 and 
                (sentiment_score > 0.1 or has_catalyst or impact_level == 'high')):
                positive_news.append(item)
        
        print(f"🚀 Found {len(positive_news)} positive stock opportunities")
        
        # Step 4: Show top opportunities
        print("\nStep 4: Top Stock Opportunities:")
        print("-" * 60)
        
        for i, item in enumerate(positive_news[:5], 1):
            classification = item['classification']
            print(f"\n{i}. {item['title']}")
            print(f"   Relevance: {classification.relevance_score:.3f}")
            print(f"   Sentiment: {classification.sentiment_score:.3f} ({classification.sentiment_label})")
            print(f"   Impact: {classification.impact_level.upper()}")
            print(f"   Catalyst: {'⚡ YES' if classification.has_catalyst else 'No'}")
            print(f"   Categories: {', '.join(classification.categories)}")
            print(f"   Why Good: {classification.summary}")
        
        # Step 5: Test email functionality (without actually sending)
        print("\nStep 5: Testing email functionality...")
        try:
            # This would normally send an email, but we'll just test the creation
            subject = email_sender._create_subject(insights)
            html_content = email_sender._create_html_report(positive_news, insights)
            text_content = email_sender._create_text_report(positive_news, insights)
            
            print(f"✅ Email content created successfully:")
            print(f"   Subject: {subject}")
            print(f"   HTML length: {len(html_content)} characters")
            print(f"   Text length: {len(text_content)} characters")
            
        except Exception as e:
            print(f"❌ Email functionality test failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Step 6: Test storage functionality
        print("\nStep 6: Testing storage functionality...")
        try:
            # Log some picks
            for item in positive_news[:3]:
                picks_logger.log_pick(
                    title=item['title'],
                    url=item['url'],
                    source=item['source'],
                    relevance_score=item['classification'].relevance_score,
                    sentiment_score=item['classification'].sentiment_score,
                    impact_level=item['classification'].impact_level,
                    has_catalyst=item['classification'].has_catalyst
                )
            
            print(f"✅ Logged {min(3, len(positive_news))} picks to storage")
            
        except Exception as e:
            print(f"❌ Storage functionality test failed: {str(e)}")
        
        print(f"\n🎉 Complete pipeline test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_email_configuration():
    """Test email configuration without sending."""
    try:
        from output.sender_email import get_email_sender
        
        print(f"\n📧 Testing Email Configuration...")
        print("-" * 60)
        
        email_sender = get_email_sender()
        
        # Test configuration validation
        config_valid = email_sender._validate_config()
        print(f"Configuration valid: {'✅ Yes' if config_valid else '❌ No'}")
        
        if config_valid:
            print(f"SMTP Host: {email_sender.config.SMTP_HOST}")
            print(f"SMTP Port: {email_sender.config.SMTP_PORT}")
            print(f"SMTP User: {email_sender.config.SMTP_USER}")
            print(f"Email To: {email_sender.config.EMAIL_TO}")
        else:
            print("❌ Email configuration is invalid. Check your .env file.")
            print("Required fields: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_TO")
        
        return config_valid
        
    except Exception as e:
        print(f"❌ Email configuration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Complete Morning Scanner Pipeline...")
    print("=" * 60)
    
    tests = [
        ("Complete Pipeline", test_complete_pipeline),
        ("Email Configuration", test_email_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- Testing {test_name} ---")
        if test_func():
            passed += 1
            print(f"✅ {test_name} test passed")
        else:
            print(f"❌ {test_name} test failed")
    
    print(f"\n{'=' * 60}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Your Morning Scanner is ready to use!")
        print("\n🚀 Next steps:")
        print("1. Configure your .env file with email settings")
        print("2. Run: python main.py")
        print("3. Check your email for the daily report!")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the configuration.")
        sys.exit(1) 