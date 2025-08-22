#!/usr/bin/env python3
"""
Test Advanced Analysis - Beyond Positive Keywords
Demonstrates how the enhanced Morning Scanner identifies strong opportunities
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_advanced_analysis():
    """Test the advanced analysis with sample news articles."""
    
    from nlp.classify import get_news_classifier
    
    print("🔬 Advanced Analysis Test - Beyond Positive Keywords")
    print("=" * 70)
    
    classifier = get_news_classifier()
    
    # Test cases showing different types of strong opportunities
    test_articles = [
        {
            'name': 'QUANTITATIVE SIGNALS',
            'title': 'Ericsson rapporterar 25% tillväxt i 5G-verksamheten',
            'snippet': 'Telekomjätten redovisar omsättningsökning på 25 procent för Q3, med förbättrade marginaler på 3 procentenheter. Kontrakt värt 2 miljarder kronor tecknades under kvartalet.',
            'why': 'Strong because: 25% revenue growth + margin improvement + large contracts'
        },
        {
            'name': 'COMPETITIVE ADVANTAGE',
            'title': 'AstraZeneca får patent för revolutionerande cancerbehandling',
            'snippet': 'Läkemedelsbolaget säkrar exklusiv licens för ny teknologi efter regulatoriskt godkännande. Innovation ger stark position på marknaden.',
            'why': 'Strong because: Patent protection + regulatory approval + exclusive position'
        },
        {
            'name': 'MANAGEMENT SIGNALS',
            'title': 'VD för Atlas Copco köper aktier för 10 miljoner',
            'snippet': 'Ledningen visar förtroende genom omfattande aktieköp. Ny strategisk plan presenteras för transformation av verksamheten.',
            'why': 'Strong because: Insider buying + strategic vision + management confidence'
        },
        {
            'name': 'MARKET TIMING',
            'title': 'Volvo överträffade förväntningarna - höjer prognos',
            'snippet': 'Biltillverkaren levererade bättre resultat än analytikernas prognoser. Guidning för helåret uppjusteras betydligt efter stark orderingång.',
            'why': 'Strong because: Earnings surprise + guidance raise + beat expectations'
        },
        {
            'name': 'VALUE SIGNALS',
            'title': 'Sandvik handlas med rabatt trots stark balansräkning',
            'snippet': 'Verkstadsbolag är undervärderat med kassarika tillgångar värt mer än börsvärdet. Substansvärde överstiger marknadspris.',
            'why': 'Strong because: Undervalued + cash rich + asset value discount'
        },
        {
            'name': 'RISK FACTORS TEST',
            'title': 'H&M varnar för förluster efter konkurrens från Shein',
            'snippet': 'Klädjätten rapporterar nedgång i försäljning. Skulder ökar medan lönsamheten försämras. Ny reglering hotar affärsmodellen.',
            'why': 'Weak because: Warning + losses + debt + competition + regulation threats'
        },
        {
            'name': 'BASIC POSITIVE KEYWORDS',
            'title': 'Svenska företag visar optimism inför framtiden',
            'snippet': 'Positiv utveckling och tillväxt väntas enligt ny undersökning. Framgång och framsteg rapporteras inom flera branscher.',
            'why': 'Comparison: Only basic positive keywords (weak signals)'
        }
    ]
    
    print("Testing 7 different types of news analysis...\n")
    
    for i, article in enumerate(test_articles, 1):
        print(f"{i}. {article['name']}")
        print("-" * 50)
        print(f"📰 Title: {article['title']}")
        print(f"📝 Snippet: {article['snippet']}")
        print(f"💡 Why Important: {article['why']}")
        
        # Classify the article
        classification = classifier.classify_news(
            title=article['title'],
            content='',
            snippet=article['snippet']
        )
        
        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"   🎯 Final Score: {classification.final_score:.3f}")
        print(f"   📈 Recommendation: {classification.recommendation}")
        print(f"   ⏰ Timeframe: {classification.timeframe}")
        print(f"   📊 Relevance: {classification.relevance_score:.3f}")
        print(f"   😊 Sentiment: {classification.sentiment_score:.3f} ({classification.sentiment_label})")
        print(f"   ⚡ Impact: {classification.impact_level.upper()}")
        print(f"   🔥 Catalyst: {'YES' if classification.has_catalyst else 'No'}")
        
        # Show advanced signals
        if classification.advanced_signals:
            print(f"   🔬 Advanced Signals ({len(classification.advanced_signals)}):")
            for signal in classification.advanced_signals:
                strength_emoji = "🔥" if signal.strength > 0.7 else "📊" if signal.strength > 0.4 else "📉" if signal.strength < 0 else "📈"
                print(f"      {strength_emoji} {signal.signal_type}: {signal.strength:.3f} - {signal.explanation}")
        else:
            print(f"   🔬 Advanced Signals: None detected")
        
        print(f"   📋 Summary: {classification.summary}")
        print()
    
    print("🎯 KEY INSIGHTS:")
    print("=" * 70)
    print("✅ STRONG OPPORTUNITIES are identified by:")
    print("   • Quantitative metrics (revenue growth, margins, large contracts)")
    print("   • Competitive advantages (patents, regulatory approvals, exclusivity)")
    print("   • Management signals (insider buying, strategic vision)")
    print("   • Market timing (earnings surprises, guidance raises)")
    print("   • Value opportunities (undervalued, cash-rich, asset discounts)")
    print()
    print("❌ RISK FACTORS are detected and penalize scores:")
    print("   • Warnings, losses, debt issues")
    print("   • Competitive threats, regulatory risks")
    print("   • Multiple negative indicators")
    print()
    print("🔍 BASIC KEYWORD ANALYSIS alone is insufficient:")
    print("   • 'Positive' words without substance = weak signals")
    print("   • Advanced analysis provides context and quantification")
    print("   • Risk-adjusted scoring prevents false positives")
    print()
    print("🚀 THE ENHANCED MORNING SCANNER NOW IDENTIFIES:")
    print("   • Companies with actual financial improvements")
    print("   • Competitive advantages that create lasting value")
    print("   • Management actions that signal confidence")
    print("   • Market timing opportunities for quick gains")
    print("   • Undervalued situations with upside potential")

def demonstrate_scoring_weights():
    """Show how different factors contribute to the final score."""
    
    print("\n" + "=" * 70)
    print("📊 SCORING METHODOLOGY BREAKDOWN")
    print("=" * 70)
    
    print("🎯 FINAL SCORE CALCULATION (0.0 to 1.0):")
    print("   • Keyword Sentiment: 30% weight")
    print("   • Relevance Score: 20% weight") 
    print("   • Advanced Signals: 40% weight")
    print("   • Risk Adjustment: -10% penalty")
    print()
    
    print("📈 ADVANCED SIGNALS HIERARCHY:")
    print("   1. Quantitative (30%): Revenue, margins, contracts, market share")
    print("   2. Timing (25%): Earnings surprises, guidance raises, upgrades")
    print("   3. Competitive (20%): Patents, regulatory moats, exclusivity")
    print("   4. Management (15%): Insider buying, leadership, strategy")
    print("   5. Tailwinds (5%): Sector trends, regulatory support")
    print("   6. Value (5%): Undervaluation, asset value, cash position")
    print()
    
    print("⏰ TIMEFRAME DETERMINATION:")
    print("   • Immediate (1-3 days): Earnings surprises, breaking news")
    print("   • Short-term (1-4 weeks): Guidance raises, analyst upgrades")
    print("   • Medium-term (1-3 months): Strategic initiatives, new products")
    print("   • Long-term (3+ months): Competitive advantages, industry trends")
    print()
    
    print("🎪 RECOMMENDATION THRESHOLDS:")
    print("   • STRONG BUY: Final score ≥ 0.8")
    print("   • BUY: Final score ≥ 0.6")
    print("   • WATCH: Final score ≥ 0.4")
    print("   • WEAK SIGNAL: Final score ≥ 0.2")
    print("   • IGNORE: Final score < 0.2")

if __name__ == "__main__":
    print("Starting Advanced Analysis Test...")
    test_advanced_analysis()
    demonstrate_scoring_weights()
    print(f"\n🎉 Advanced analysis test completed!")
    print("🚀 Your Morning Scanner now goes far beyond just positive keywords!") 