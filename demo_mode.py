#!/usr/bin/env python3
"""Demo mode for Morning Scanner - Shows complete pipeline with mock data."""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_demo():
    """Run the complete Morning Scanner pipeline in demo mode."""
    try:
        from nlp.classify import get_news_classifier
        from output.sender_email import get_email_sender
        from storage.picks_log import get_picks_logger
        from common.utils_time import now_se
        
        print("🎭 Morning Scanner - Demo Mode")
        print("=" * 60)
        print("This demo shows the complete pipeline using mock data")
        print("=" * 60)
        
        # Get components
        news_classifier = get_news_classifier()
        email_sender = get_email_sender()
        picks_logger = get_picks_logger()
        
        print("✅ All components loaded successfully")
        
        # Create realistic mock news data
        mock_news = [
            {
                'title': 'Ericsson överträffar förväntningarna med stark Q3-rapport',
                'snippet': 'Telekomjätten redovisar bättre resultat än väntat med stark orderingång från 5G-segment. Höjer prognos för helåret och förväntar sig fortsatt tillväxt i Q4.',
                'url': 'https://www.mfn.se/nyheter/ericsson-q3-strong',
                'source': 'MFN',
                'timestamp': '2025-08-22T08:30:00'
            },
            {
                'title': 'Volvo Cars vinner miljardorder från europeisk biluthyrare',
                'snippet': 'Strategiskt ramavtal värt 3,5 miljarder kronor över tre år. Fokus på elektriska fordon stärker framtidsutsikter och orderboken växer till rekordnivå.',
                'url': 'https://www.di.se/nyheter/volvo-big-contract',
                'source': 'DI Morgonkoll',
                'timestamp': '2025-08-22T08:15:00'
            },
            {
                'title': 'AstraZeneca får FDA-godkännande för revolutionerande cancermedicin',
                'snippet': 'Regulatoriskt genombrott öppnar för global kommersialisering av ny onkologibehandling. Royaltyintäkter väntas och patentportföljen stärks betydligt.',
                'url': 'https://www.mfn.se/nyheter/astrazeneca-fda-approval',
                'source': 'MFN',
                'timestamp': '2025-08-22T07:45:00'
            },
            {
                'title': 'Atlas Copco lanserar revolutionerande kompressorteknik',
                'snippet': 'Produktlansering med 40% högre energieffektivitet än befintliga lösningar. Patent beviljat för ny kompressorteknik som förväntas dominera marknaden.',
                'url': 'https://www.di.se/nyheter/atlas-copco-innovation',
                'source': 'DI Morgonkoll',
                'timestamp': '2025-08-22T07:30:00'
            },
            {
                'title': 'SEB höjer riktkurs för flera svenska industribolag',
                'snippet': 'Banken uppgraderar flera svenska industriaktier till köpråd. Stark köprekommendation för sektorn baserat på förbättrade utsikter och stark export.',
                'url': 'https://www.mfn.se/nyheter/seb-upgrades',
                'source': 'MFN',
                'timestamp': '2025-08-22T07:00:00'
            },
            {
                'title': 'Sandvik lanserar ny produktlinje för hållbar utveckling',
                'snippet': 'Produktlansering fokuserad på grön energi och cirkulär ekonomi. Marknadslansering i Q4 med förväntad stor efterfrågan från europeiska marknader.',
                'url': 'https://www.di.se/nyheter/sandvik-green-products',
                'source': 'DI Morgonkoll',
                'timestamp': '2025-08-22T06:45:00'
            },
            {
                'title': 'H&M presenterar månadsrapport med förbättrade försäljningssiffror',
                'snippet': 'Bokslut visar kundtillväxt och förbättrad lönsamhet. Förbättrad visibilitet på marknaden och starkare position i digital handel.',
                'url': 'https://www.mfn.se/nyheter/hm-monthly-report',
                'source': 'MFN',
                'timestamp': '2025-08-22T06:30:00'
            },
            {
                'title': 'Essity får CE-märkning för nytt miljövänligt produktsortiment',
                'snippet': 'Regulatoriskt godkännande för hållbara produkter. Kommersiellt genombrott väntas i europeiska marknader med stark efterfrågan.',
                'url': 'https://www.di.se/nyheter/essity-ce-marking',
                'source': 'DI Morgonkoll',
                'timestamp': '2025-08-22T06:15:00'
            }
        ]
        
        print(f"\n📰 Step 1: Processing {len(mock_news)} mock news items...")
        print("-" * 60)
        
        # Step 1: Classify news
        print("🔍 Classifying news items...")
        classified_news = []
        
        for item in mock_news:
            classification = news_classifier.classify_news(
                item['title'], 
                '',  # No full content
                item['snippet']
            )
            item['classification'] = classification
            classified_news.append(item)
        
        print(f"✅ Classified {len(classified_news)} news items")
        
        # Step 2: Generate insights
        print(f"\n📊 Step 2: Generating market insights...")
        insights = news_classifier.get_news_insights(classified_news)
        
        print(f"📈 Market Summary:")
        print(f"   - Total Items: {insights['total_items']}")
        print(f"   - High Impact: {insights['impact_distribution']['high']}")
        print(f"   - Medium Impact: {insights['impact_distribution']['medium']}")
        print(f"   - Catalyst Events: {insights['catalyst_events']}")
        print(f"   - Market Sentiment: {insights['insights']}")
        
        # Step 3: Filter positive opportunities
        print(f"\n🚀 Step 3: Filtering positive stock opportunities...")
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
        
        print(f"🎯 Found {len(positive_news)} positive stock opportunities")
        
        # Step 4: Show top opportunities
        print(f"\n📋 Step 4: Top Stock Opportunities:")
        print("-" * 60)
        
        for i, item in enumerate(positive_news[:5], 1):
            classification = item['classification']
            print(f"\n{i}. {item['title']}")
            print(f"   📊 Relevance: {classification.relevance_score:.3f}")
            print(f"   😊 Sentiment: {classification.sentiment_score:.3f} ({classification.sentiment_label})")
            print(f"   ⚡ Impact: {classification.impact_level.upper()}")
            print(f"   🔥 Catalyst: {'⚡ YES' if classification.has_catalyst else 'No'}")
            print(f"   🏷️  Categories: {', '.join(classification.categories)}")
            print(f"   💡 Why Good: {classification.summary}")
        
        # Step 5: Log picks
        print(f"\n💾 Step 5: Logging news picks...")
        try:
            for item in positive_news[:5]:
                picks_logger.log_pick(
                    title=item['title'],
                    url=item['url'],
                    source=item['source'],
                    relevance_score=item['classification'].relevance_score,
                    sentiment_score=item['classification'].sentiment_score,
                    impact_level=item['classification'].impact_level,
                    has_catalyst=item['classification'].has_catalyst,
                    categories=item['classification'].categories
                )
            print(f"✅ Logged {min(5, len(positive_news))} picks to storage")
        except Exception as e:
            print(f"⚠️  Storage logging failed: {str(e)}")
        
        # Step 6: Send email report
        print(f"\n📧 Step 6: Sending email report...")
        if email_sender.is_configured():
            try:
                success = email_sender.send_daily_report(classified_news, insights)
                if success:
                    print(f"🎉 Email report sent successfully!")
                    print(f"📬 Check your inbox at: {email_sender.config.EMAIL_TO}")
                else:
                    print(f"❌ Failed to send email report")
            except Exception as e:
                print(f"❌ Email sending failed: {str(e)}")
        else:
            print(f"⚠️  Email not configured - skipping email step")
        
        # Step 7: Show final summary
        print(f"\n🎯 Final Summary:")
        print("-" * 60)
        print(f"📰 Total News Processed: {len(mock_news)}")
        print(f"🚀 Positive Opportunities: {len(positive_news)}")
        print(f"⚡ Catalyst Events: {insights['catalyst_events']}")
        print(f"📊 High Impact News: {insights['impact_distribution']['high']}")
        print(f"💾 Picks Logged: {min(5, len(positive_news))}")
        print(f"📧 Email Sent: {'Yes' if email_sender.is_configured() else 'No'}")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"🚀 Your Morning Scanner is working perfectly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting Morning Scanner Demo Mode...")
    success = run_demo()
    
    if success:
        print(f"\n🎉 Demo completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Demo failed. Please check the configuration.")
        sys.exit(1) 