#!/usr/bin/env python3
"""Test script for Swedish Financial Keywords system."""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_swedish_keywords():
    """Test the Swedish financial keywords system."""
    try:
        from nlp.keywords import get_keyword_analyzer
        from nlp.classify import get_news_classifier
        
        print("🧪 Testing Swedish Financial Keywords System")
        print("=" * 60)
        
        # Get keyword analyzer
        keyword_analyzer = get_keyword_analyzer()
        print(f"✅ Keyword analyzer loaded: {len(keyword_analyzer.POSITIVE_KEYWORDS)} positive, "
              f"{len(keyword_analyzer.NEGATIVE_KEYWORDS)} negative, "
              f"{len(keyword_analyzer.CATALYST_KEYWORDS)} catalyst keywords")
        
        # Test news classifier
        news_classifier = get_news_classifier()
        print("✅ News classifier loaded")
        
        # Test sample news items
        test_news = [
            {
                'title': 'Ericsson överträffar förväntningarna med stark rapport',
                'snippet': 'Bolaget höjer prognos och guidning över väntan',
                'content': 'Ericsson presenterar rekordresultat med vinstlyft och marginallyft. Stark orderingång och ny kund.'
            },
            {
                'title': 'Volvo sänker prognos på grund av svag efterfrågan',
                'snippet': 'Vinstvarning och sänkt guidning för kommande kvartal',
                'content': 'Volvo missar förväntningarna med svag rapport. Produktionsproblem och leveransproblem.'
            },
            {
                'title': 'AstraZeneca får FDA-godkännande för nytt läkemedel',
                'snippet': 'Regulatoriskt godkännande öppnar för kommersialisering',
                'content': 'AstraZeneca får FDA-godkännande för nytt läkemedel. Klinisk framgång i fas 3.'
            },
            {
                'title': 'H&M presenterar månadsrapport med försäljningssiffror',
                'snippet': 'Bokslut och kundtillväxt i fokus',
                'content': 'H&M uppdaterar marknaden med månadsrapport. Försäljningssiffror och kundtillväxt.'
            },
            {
                'title': 'Generisk nyhet om marknaden',
                'snippet': 'Standard marknadsutveckling utan särskilda händelser',
                'content': 'Marknaden utvecklas enligt förväntningarna. Inga större förändringar rapporteras.'
            }
        ]
        
        print(f"\n📰 Analyzing {len(test_news)} test news items...")
        print("-" * 60)
        
        for i, news in enumerate(test_news, 1):
            print(f"\n📰 News Item {i}: {news['title']}")
            print(f"   Snippet: {news['snippet']}")
            
            # Classify the news
            classification = news_classifier.classify_news(
                news['title'], 
                news.get('content', ''), 
                news['snippet']
            )
            
            print(f"   📊 Classification: {classification.summary}")
            print(f"   🎯 Relevance Score: {classification.relevance_score:.3f}")
            print(f"   😊 Sentiment: {classification.sentiment_score:.3f} ({classification.sentiment_label})")
            print(f"   ⚡ Impact Level: {classification.impact_level.upper()}")
            
            if classification.categories:
                print(f"   🏷️  Categories: {', '.join(classification.categories)}")
            
            if classification.industry_relevance:
                relevant_industries = [ind for ind, score in classification.industry_relevance.items() if score > 0.1]
                if relevant_industries:
                    print(f"   🏭 Industry Relevance: {', '.join(relevant_industries)}")
        
        # Test keyword extraction
        print(f"\n🔍 Testing Keyword Extraction...")
        print("-" * 60)
        
        sample_text = "Ericsson överträffar förväntningarna med stark rapport och höjer prognos. Ny kund och strategiskt avtal."
        keywords = keyword_analyzer.extract_keywords(sample_text)
        
        print(f"Sample text: {sample_text}")
        print(f"Positive keywords: {[m.keyword for m in keywords['positive']]}")
        print(f"Negative keywords: {[m.keyword for m in keywords['negative']]}")
        print(f"Catalyst keywords: {[m.keyword for m in keywords['catalyst']]}")
        
        # Test sentiment analysis
        sentiment_score = keyword_analyzer.calculate_sentiment_score(sample_text)
        print(f"Sentiment score: {sentiment_score:.3f}")
        
        # Test keyword summary
        summary = keyword_analyzer.get_keyword_summary(sample_text)
        print(f"Keyword summary: {summary['sentiment_label']} tone, {summary['counts']['total']} total keywords")
        
        # Test news insights
        print(f"\n📈 Testing News Insights...")
        print("-" * 60)
        
        # Classify all test news
        classified_news = []
        for news in test_news:
            classification = news_classifier.classify_news(
                news['title'], 
                news.get('content', ''), 
                news['snippet']
            )
            news['classification'] = classification
            classified_news.append(news)
        
        insights = news_classifier.get_news_insights(classified_news)
        print(f"Total items: {insights['total_items']}")
        print(f"Impact distribution: {insights['impact_distribution']}")
        print(f"Sentiment distribution: {insights['sentiment_distribution']}")
        print(f"Category distribution: {insights['category_distribution']}")
        print(f"Catalyst events: {insights['catalyst_events']}")
        print(f"Insights: {insights['insights']}")
        
        print(f"\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_keyword_patterns():
    """Test regex patterns for keyword matching."""
    try:
        from nlp.keywords import get_keyword_analyzer
        
        print(f"\n🔍 Testing Keyword Patterns...")
        print("-" * 60)
        
        keyword_analyzer = get_keyword_analyzer()
        
        # Test positive pattern
        test_text = "Bolaget har stark orderingång och höjer prognos"
        positive_matches = keyword_analyzer.positive_pattern.findall(test_text)
        print(f"Positive pattern test: '{test_text}' -> {positive_matches}")
        
        # Test negative pattern
        test_text = "Vinstvarning och sänkt guidning"
        negative_matches = keyword_analyzer.negative_pattern.findall(test_text)
        print(f"Negative pattern test: '{test_text}' -> {negative_matches}")
        
        # Test catalyst pattern
        test_text = "Bokslut och månadsrapport"
        catalyst_matches = keyword_analyzer.catalyst_pattern.findall(test_text)
        print(f"Catalyst pattern test: '{test_text}' -> {catalyst_matches}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pattern test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Swedish Financial Keywords System...")
    print("=" * 60)
    
    tests = [
        ("Swedish Keywords", test_swedish_keywords),
        ("Keyword Patterns", test_keyword_patterns)
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
        print("🎉 All tests passed! Swedish keywords system is working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the implementation.")
        sys.exit(1) 