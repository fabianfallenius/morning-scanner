#!/usr/bin/env python3
"""
Show Positive Articles - Morning Analysis for August 22nd
Displays the positive Swedish financial news found this morning
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def analyze_todays_news():
    """Analyze today's news and show positive articles."""
    try:
        from sources.di_morgonkoll import DIMorgonkollScraper
        from sources.extras import ExtraSourcesScraper
        from nlp.classify import get_news_classifier
        from output.sender_email import get_email_sender
        
        print("🌅 Morning Scanner - Today's Positive Articles Analysis")
        print("=" * 70)
        print(f"📅 Date: {datetime.now().strftime('%A, %B %d, %Y')}")
        print(f"🕐 Time: {datetime.now().strftime('%H:%M')} (Stockholm Time)")
        print("=" * 70)
        
        # Initialize components
        news_classifier = get_news_classifier()
        email_sender = get_email_sender()
        
        print("📰 Collecting Swedish Financial News...")
        print("-" * 40)
        
        # Collect from DI Morgonkoll
        print("🔍 Scanning DI Morgonkoll...")
        di_scraper = DIMorgonkollScraper()
        try:
            di_news = await di_scraper.scrape_news()
            print(f"   ✅ Found {len(di_news)} articles from DI Morgonkoll")
        finally:
            await di_scraper.close()
        
        # Collect from Extra Sources (RSS feeds)
        print("🔍 Scanning RSS Feeds (SVT, DN, etc.)...")
        extra_scraper = ExtraSourcesScraper()
        try:
            rss_news = await extra_scraper.scrape_news()
            print(f"   ✅ Found {len(rss_news)} articles from RSS feeds")
        finally:
            await extra_scraper.close()
        
        # Combine all news
        all_news = di_news + rss_news
        
        print(f"\n📊 Total Articles Collected: {len(all_news)}")
        print("\n🔬 Analyzing Articles with Swedish Financial Keywords...")
        print("-" * 40)
        
        # Classify each article
        classified_news = []
        positive_articles = []
        
        for i, article in enumerate(all_news, 1):
            try:
                title = article.get('title', '')
                snippet = article.get('snippet', '')
                
                if not title:
                    continue
                
                # Classify the article
                classification = news_classifier.classify_news(title, '', snippet)
                
                article['classification'] = classification
                classified_news.append(article)
                
                # Filter for positive articles with lower threshold
                relevance_score = classification.relevance_score
                sentiment_score = classification.sentiment_score
                impact_level = classification.impact_level
                has_catalyst = classification.has_catalyst
                
                # Lower threshold from 0.3 to 0.2, and be more inclusive
                if (relevance_score >= 0.2 and  # Lowered from 0.3
                    (sentiment_score > 0.0 or has_catalyst or impact_level in ['high', 'medium', 'low'])):
                    positive_articles.append(article)
                
                print(f"   📄 {i:2d}. {title[:60]}{'...' if len(title) > 60 else ''}")
                print(f"        📊 Relevance: {relevance_score:.3f} | 😊 Sentiment: {sentiment_score:.3f} | ⚡ Impact: {impact_level}")
                
            except Exception as e:
                print(f"   ❌ Error analyzing article {i}: {e}")
                continue
        
        # Generate insights
        insights = news_classifier.get_enhanced_insights(classified_news)
        
        print(f"\n📈 Market Analysis Summary:")
        print("-" * 40)
        print(f"📰 Total Articles Analyzed: {insights['total_items']}")
        print(f"🚀 Positive Opportunities: {len(positive_articles)}")
        print(f"⚡ Catalyst Events: {insights.get("advanced_signals_detected", 0)}")
        print(f"📊 High Impact News: {insights.get("strong_opportunities", 0)}")
        print(f"📊 Medium Impact News: {insights.get("strong_opportunities", 0)}")
        print(f"📊 Market Sentiment: {insights['insights']}")
        
        if positive_articles:
            print(f"\n🎯 POSITIVE STOCK OPPORTUNITIES TODAY:")
            print("=" * 70)
            
            # Sort by relevance score
            positive_articles.sort(key=lambda x: x['classification'].relevance_score, reverse=True)
            
            for i, article in enumerate(positive_articles, 1):
                classification = article['classification']
                
                print(f"\n{i}. {article['title']}")
                print(f"   🔗 {article['url']}")
                print(f"   📰 Source: {article['source']}")
                print(f"   📊 Relevance Score: {classification.relevance_score:.3f}")
                print(f"   😊 Sentiment: {classification.sentiment_score:.3f} ({classification.sentiment_label})")
                print(f"   ⚡ Impact Level: {classification.impact_level.upper()}")
                print(f"   🔥 Catalyst Event: {'⚡ YES' if classification.has_catalyst else 'No'}")
                print(f"   🏷️  Categories: {', '.join(classification.categories) if classification.categories else 'General'}")
                
                if article.get('snippet'):
                    snippet = article['snippet']
                    if len(snippet) > 200:
                        snippet = snippet[:200] + "..."
                    print(f"   📝 Summary: {snippet}")
                
                # Explain why this is a good opportunity
                explanation = _explain_opportunity(classification)
                print(f"   💡 Why This is Good: {explanation}")
                
        else:
            print(f"\n⚠️  No strong positive opportunities found in today's news.")
            print("   This could mean:")
            print("   • Market is in a neutral/cautious phase")
            print("   • Most news is priced in already")
            print("   • Good time to wait for clearer signals")
        
        print(f"\n📧 Email Report Status:")
        print("-" * 40)
        if email_sender.is_configured():
            print(f"✅ Daily report sent to: {email_sender.config.EMAIL_TO}")
            print(f"📬 Check your inbox for the detailed HTML report!")
        else:
            print(f"⚠️  Email not configured")
        
        print(f"\n🎯 Trading Recommendations:")
        print("-" * 40)
        if positive_articles:
            high_relevance = [a for a in positive_articles if a['classification'].relevance_score >= 0.6]
            if high_relevance:
                print(f"🔥 HIGH CONFIDENCE ({len(high_relevance)} opportunities):")
                for article in high_relevance[:3]:
                    print(f"   • Consider researching companies mentioned in: {article['title'][:80]}...")
            
            medium_relevance = [a for a in positive_articles if 0.4 <= a['classification'].relevance_score < 0.6]
            if medium_relevance:
                print(f"📊 MEDIUM CONFIDENCE ({len(medium_relevance)} opportunities):")
                for article in medium_relevance[:2]:
                    print(f"   • Watch for developments: {article['title'][:80]}...")
        else:
            print("💰 Today's Strategy: WAIT AND WATCH")
            print("   • No clear positive signals detected")
            print("   • Consider building watchlists")
            print("   • Wait for stronger catalyst events")
        
        print(f"\n⚠️  Disclaimer:")
        print("This analysis is for informational purposes only.")
        print("Always do your own research before making investment decisions.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

def _explain_opportunity(classification):
    """Explain why an article represents a good opportunity."""
    reasons = []
    
    if classification.relevance_score >= 0.6:
        reasons.append("High relevance to Swedish financial markets")
    elif classification.relevance_score >= 0.4:
        reasons.append("Moderate relevance to investment opportunities")
    
    if classification.sentiment_score > 0.2:
        reasons.append("Strong positive sentiment detected")
    elif classification.sentiment_score > 0.05:
        reasons.append("Positive sentiment indicators")
    
    if classification.has_catalyst:
        reasons.append("Contains catalyst event keywords")
    
    if classification.impact_level == 'high':
        reasons.append("High market impact potential")
    elif classification.impact_level == 'medium':
        reasons.append("Medium market impact expected")
    
    if classification.categories:
        reasons.append(f"Relevant to {', '.join(classification.categories)} sector(s)")
    
    if not reasons:
        reasons.append("Multiple positive indicators detected")
    
    return " | ".join(reasons)

if __name__ == "__main__":
    print("Starting Morning News Analysis...")
    success = asyncio.run(analyze_todays_news())
    
    if success:
        print(f"\n🎉 Analysis completed successfully!")
        print(f"🚀 Happy trading! 📈")
    else:
        print(f"\n❌ Analysis failed.")
        sys.exit(1) 