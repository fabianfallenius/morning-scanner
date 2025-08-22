#!/usr/bin/env python3
"""News Classification for Morning Scanner - Now with Advanced Analysis"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .keywords import get_keyword_analyzer, KeywordMatch
from .advanced_analysis import get_advanced_analyzer, AdvancedSignal

logger = logging.getLogger(__name__)


@dataclass
class NewsClassification:
    """Enhanced news classification with advanced signals."""
    # Basic classification
    relevance_score: float
    sentiment_score: float
    sentiment_label: str
    impact_level: str
    has_catalyst: bool
    categories: List[str]
    summary: str
    
    # Advanced signals
    advanced_signals: List[AdvancedSignal] = field(default_factory=list)
    advanced_score: float = 0.0
    risk_adjusted_score: float = 0.0
    signal_confidence: float = 0.0
    
    # Combined scoring
    final_score: float = 0.0
    recommendation: str = ""
    timeframe: str = ""
    
    # Matched keywords for reference
    positive_keywords: List[KeywordMatch] = field(default_factory=list)
    negative_keywords: List[KeywordMatch] = field(default_factory=list)
    catalyst_keywords: List[KeywordMatch] = field(default_factory=list)


class NewsClassifier:
    """Enhanced news classifier with advanced analysis beyond keywords."""
    
    def __init__(self):
        self.keyword_analyzer = get_keyword_analyzer()
        self.advanced_analyzer = get_advanced_analyzer()
        logger.info("Enhanced news classifier initialized")
    
    def classify_news(self, title: str, content: str = "", snippet: str = "") -> NewsClassification:
        """
        Classify news with both keyword analysis and advanced signals.
        
        Args:
            title: News article title
            content: Full article content (if available)
            snippet: Article snippet/summary
            
        Returns:
            Enhanced NewsClassification with advanced signals
        """
        try:
            # Step 1: Basic keyword analysis
            positive_keywords = self.keyword_analyzer.extract_positive_keywords(title, content, snippet)
            negative_keywords = self.keyword_analyzer.extract_negative_keywords(title, content, snippet)
            catalyst_keywords = self.keyword_analyzer.extract_catalyst_keywords(title, content, snippet)
            
            # Step 2: Advanced signal analysis
            advanced_signals = self.advanced_analyzer.analyze_advanced_signals(title, content, snippet)
            advanced_metrics = self.advanced_analyzer.calculate_advanced_score(advanced_signals)
            
            # Step 3: Calculate basic scores
            relevance_score = self._calculate_relevance_score(
                positive_keywords, negative_keywords, catalyst_keywords, advanced_signals
            )
            sentiment_score = self.keyword_analyzer.calculate_sentiment_score(
                positive_keywords, negative_keywords
            )
            
            # Step 4: Determine impact and categorization
            impact_level = self._determine_enhanced_impact_level(
                relevance_score, sentiment_score, catalyst_keywords, advanced_signals
            )
            has_catalyst = len(catalyst_keywords) > 0 or any(
                'timing_' in signal.signal_type for signal in advanced_signals
            )
            categories = self._classify_enhanced_categories(
                positive_keywords, catalyst_keywords, advanced_signals
            )
            
            # Step 5: Combine scores for final recommendation
            final_score, recommendation, timeframe = self._calculate_final_score(
                relevance_score, sentiment_score, advanced_metrics, advanced_signals
            )
            
            # Step 6: Create summary
            summary = self._create_enhanced_summary(
                relevance_score, sentiment_score, impact_level, has_catalyst,
                categories, advanced_signals, len(positive_keywords), 
                len(negative_keywords), len(catalyst_keywords)
            )
            
            return NewsClassification(
                relevance_score=relevance_score,
                sentiment_score=sentiment_score,
                sentiment_label=self._get_sentiment_label(sentiment_score),
                impact_level=impact_level,
                has_catalyst=has_catalyst,
                categories=categories,
                summary=summary,
                advanced_signals=advanced_signals,
                advanced_score=advanced_metrics['advanced_score'],
                risk_adjusted_score=advanced_metrics['risk_adjusted_score'],
                signal_confidence=advanced_metrics['confidence'],
                final_score=final_score,
                recommendation=recommendation,
                timeframe=timeframe,
                positive_keywords=positive_keywords,
                negative_keywords=negative_keywords,
                catalyst_keywords=catalyst_keywords
            )
            
        except Exception as e:
            logger.error(f"Error classifying news: {e}")
            return self._create_empty_enhanced_classification()
    
    def _calculate_relevance_score(self, positive_keywords: List[KeywordMatch], 
                                 negative_keywords: List[KeywordMatch],
                                 catalyst_keywords: List[KeywordMatch],
                                 advanced_signals: List[AdvancedSignal]) -> float:
        """Enhanced relevance calculation including advanced signals."""
        
        # Basic keyword relevance (40% weight)
        keyword_relevance = self.keyword_analyzer.calculate_relevance_score(
            positive_keywords, negative_keywords, catalyst_keywords
        ) * 0.4
        
        # Advanced signals relevance (60% weight)
        signal_relevance = 0.0
        if advanced_signals:
            # Weight different signal types
            signal_weights = {
                'quantitative': 0.3,
                'timing': 0.25,
                'competitive': 0.2,
                'management': 0.15,
                'tailwind': 0.05,
                'value': 0.05
            }
            
            weighted_score = 0.0
            total_weight = 0.0
            
            for signal in advanced_signals:
                if signal.strength > 0:  # Ignore negative signals for relevance
                    signal_category = signal.signal_type.split('_')[0]
                    weight = signal_weights.get(signal_category, 0.1)
                    weighted_score += signal.strength * weight * signal.confidence
                    total_weight += weight * signal.confidence
            
            if total_weight > 0:
                signal_relevance = (weighted_score / total_weight) * 0.6
        
        return min(1.0, keyword_relevance + signal_relevance)
    
    def _determine_enhanced_impact_level(self, relevance_score: float, sentiment_score: float,
                                       catalyst_keywords: List[KeywordMatch],
                                       advanced_signals: List[AdvancedSignal]) -> str:
        """Enhanced impact level determination."""
        
        # Check for high-impact advanced signals
        high_impact_signals = [
            signal for signal in advanced_signals 
            if signal.strength > 0.7 and signal.signal_type.startswith(('quantitative_', 'timing_'))
        ]
        
        # Check for immediate timing signals
        immediate_signals = [
            signal for signal in advanced_signals
            if signal.timeframe == 'immediate' and signal.strength > 0.6
        ]
        
        if high_impact_signals or immediate_signals:
            return 'high'
        elif relevance_score > 0.7 and (sentiment_score > 0.3 or len(catalyst_keywords) > 1):
            return 'high'
        elif relevance_score > 0.4 and (sentiment_score > 0.1 or len(catalyst_keywords) > 0):
            return 'medium'
        else:
            return 'low'
    
    def _classify_enhanced_categories(self, positive_keywords: List[KeywordMatch],
                                    catalyst_keywords: List[KeywordMatch],
                                    advanced_signals: List[AdvancedSignal]) -> List[str]:
        """Enhanced category classification."""
        
        # Start with basic keyword categories
        categories = self.keyword_analyzer.classify_categories(positive_keywords, catalyst_keywords)
        
        # Add categories from advanced signals
        signal_categories = []
        for signal in advanced_signals:
            if signal.strength > 0.5:
                if 'quantitative' in signal.signal_type:
                    signal_categories.append('financial_metrics')
                elif 'competitive' in signal.signal_type:
                    signal_categories.append('competitive_advantage')
                elif 'management' in signal.signal_type:
                    signal_categories.append('governance')
                elif 'timing' in signal.signal_type:
                    signal_categories.append('market_timing')
                elif 'value' in signal.signal_type:
                    signal_categories.append('value_opportunity')
        
        # Combine and deduplicate
        all_categories = list(set(categories + signal_categories))
        return all_categories[:5]  # Limit to top 5 categories
    
    def _calculate_final_score(self, relevance_score: float, sentiment_score: float,
                             advanced_metrics: Dict[str, float],
                             advanced_signals: List[AdvancedSignal]) -> tuple[float, str, str]:
        """Calculate final combined score and recommendation."""
        
        # Weight the different components
        keyword_weight = 0.3
        relevance_weight = 0.2
        advanced_weight = 0.4
        risk_adjustment_weight = 0.1
        
        # Calculate components
        keyword_component = sentiment_score * keyword_weight
        relevance_component = relevance_score * relevance_weight
        advanced_component = advanced_metrics['risk_adjusted_score'] * advanced_weight
        
        # Risk adjustment
        risk_penalty = advanced_metrics.get('risk_factors', 0) * risk_adjustment_weight
        
        # Final score
        final_score = max(0.0, 
            keyword_component + relevance_component + advanced_component - risk_penalty
        )
        
        # Determine recommendation and timeframe
        recommendation, timeframe = self._get_recommendation(final_score, advanced_signals)
        
        return final_score, recommendation, timeframe
    
    def _get_recommendation(self, final_score: float, 
                          advanced_signals: List[AdvancedSignal]) -> tuple[str, str]:
        """Get trading recommendation and timeframe."""
        
        # Check for immediate signals
        immediate_signals = [s for s in advanced_signals if s.timeframe == 'immediate' and s.strength > 0.6]
        short_term_signals = [s for s in advanced_signals if s.timeframe == 'short-term' and s.strength > 0.5]
        
        if final_score >= 0.8:
            recommendation = "STRONG BUY"
        elif final_score >= 0.6:
            recommendation = "BUY"
        elif final_score >= 0.4:
            recommendation = "WATCH"
        elif final_score >= 0.2:
            recommendation = "WEAK SIGNAL"
        else:
            recommendation = "IGNORE"
        
        # Determine timeframe
        if immediate_signals:
            timeframe = "Immediate (1-3 days)"
        elif short_term_signals:
            timeframe = "Short-term (1-4 weeks)"
        elif final_score >= 0.6:
            timeframe = "Medium-term (1-3 months)"
        else:
            timeframe = "Long-term (3+ months)"
        
        return recommendation, timeframe
    
    def _create_enhanced_summary(self, relevance_score: float, sentiment_score: float,
                               impact_level: str, has_catalyst: bool, categories: List[str],
                               advanced_signals: List[AdvancedSignal], pos_count: int,
                               neg_count: int, cat_count: int) -> str:
        """Create enhanced summary including advanced signals."""
        
        summary_parts = [
            f"Impact: {impact_level.upper()}",
            f"Tone: {self._get_sentiment_label(sentiment_score)}",
            f"Categories: {', '.join(categories[:3]) if categories else 'General'}",
            f"Keywords: {pos_count}+ {neg_count}- {cat_count}⚡"
        ]
        
        # Add advanced signal summary
        if advanced_signals:
            signal_summary = self.advanced_analyzer.get_signal_summary(advanced_signals)
            summary_parts.append(f"Signals: {signal_summary}")
        
        if has_catalyst:
            summary_parts.append("⚡ CATALYST EVENT")
        
        return " | ".join(summary_parts)
    
    def _get_sentiment_label(self, sentiment_score: float) -> str:
        """Get sentiment label from score."""
        if sentiment_score > 0.3:
            return "Very Positive"
        elif sentiment_score > 0.1:
            return "Positive"
        elif sentiment_score > -0.1:
            return "Neutral"
        elif sentiment_score > -0.3:
            return "Negative"
        else:
            return "Very Negative"
    
    def _create_empty_enhanced_classification(self) -> NewsClassification:
        """Create empty classification for error cases."""
        return NewsClassification(
            relevance_score=0.0,
            sentiment_score=0.0,
            sentiment_label="Unknown",
            impact_level="low",
            has_catalyst=False,
            categories=[],
            summary="Analysis failed",
            advanced_signals=[],
            advanced_score=0.0,
            risk_adjusted_score=0.0,
            signal_confidence=0.0,
            final_score=0.0,
            recommendation="IGNORE",
            timeframe="Unknown"
        )
    
    def filter_news_by_enhanced_criteria(self, classified_news: List[Dict]) -> List[Dict]:
        """Filter news using enhanced criteria including advanced signals."""
        positive_news = []
        
        for item in classified_news:
            classification = item.get('classification')
            if not classification:
                continue
            
            # Enhanced filtering criteria
            meets_criteria = (
                classification.final_score >= 0.4 or  # Strong overall signal
                classification.advanced_score >= 0.5 or  # Strong advanced signals
                (classification.relevance_score >= 0.3 and classification.has_catalyst) or  # Catalyst with relevance
                classification.recommendation in ["STRONG BUY", "BUY"]  # Direct recommendation
            )
            
            if meets_criteria:
                positive_news.append(item)
        
        # Sort by final score
        positive_news.sort(key=lambda x: x['classification'].final_score, reverse=True)
        return positive_news
    
    def get_enhanced_insights(self, classified_news: List[Dict]) -> Dict[str, Any]:
        """Generate enhanced market insights including advanced signals."""
        if not classified_news:
            return {
                'total_items': 0,
                'strong_opportunities': 0,
                'advanced_signals_detected': 0,
                'insights': 'No news to analyze'
            }
        
        # Enhanced analysis
        total_items = len(classified_news)
        strong_opportunities = len([
            item for item in classified_news 
            if item.get('classification', {}).final_score >= 0.6
        ])
        
        # Count advanced signals
        all_signals = []
        for item in classified_news:
            classification = item.get('classification')
            if classification and hasattr(classification, 'advanced_signals'):
                all_signals.extend(classification.advanced_signals)
        
        signal_types = {}
        for signal in all_signals:
            signal_category = signal.signal_type.split('_')[0]
            signal_types[signal_category] = signal_types.get(signal_category, 0) + 1
        
        # Generate insights
        insights_parts = []
        if strong_opportunities > 0:
            insights_parts.append(f"🚀 {strong_opportunities} strong opportunities detected")
        if signal_types:
            top_signals = sorted(signal_types.items(), key=lambda x: x[1], reverse=True)[:3]
            signal_summary = ", ".join([f"{sig}({count})" for sig, count in top_signals])
            insights_parts.append(f"📊 Advanced signals: {signal_summary}")
        
        return {
            'total_items': total_items,
            'strong_opportunities': strong_opportunities,
            'advanced_signals_detected': len(all_signals),
            'signal_breakdown': signal_types,
            'insights': " | ".join(insights_parts) if insights_parts else "Market analysis complete"
        }


# Global instance
news_classifier = NewsClassifier()


def get_news_classifier() -> NewsClassifier:
    """Get the global enhanced news classifier instance."""
    return news_classifier 