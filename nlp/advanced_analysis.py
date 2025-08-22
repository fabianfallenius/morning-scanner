#!/usr/bin/env python3
"""
Advanced News Analysis - Beyond Positive Keywords
Identifies strong stock opportunities using multiple sophisticated factors
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import math

logger = logging.getLogger(__name__)


@dataclass
class AdvancedSignal:
    """Represents an advanced trading signal beyond basic sentiment."""
    signal_type: str
    strength: float  # 0.0 to 1.0
    explanation: str
    confidence: float  # 0.0 to 1.0
    timeframe: str  # "immediate", "short-term", "medium-term", "long-term"


class AdvancedAnalyzer:
    """Advanced analysis beyond positive keywords."""
    
    def __init__(self):
        self._setup_patterns()
        logger.info("Advanced analyzer initialized")
    
    def _setup_patterns(self):
        """Setup pattern matching for advanced signals."""
        
        # 1. QUANTITATIVE SIGNALS (Numbers that matter)
        self.quantitative_patterns = {
            'revenue_growth': {
                'patterns': [
                    r'intäkter.*?(\d+).*?procent',
                    r'omsättning.*?ökade.*?(\d+).*?%',
                    r'försäljning.*?upp.*?(\d+).*?procent',
                    r'revenue.*?grew.*?(\d+).*?%'
                ],
                'threshold': 10,  # 10%+ growth is significant
                'weight': 0.8
            },
            'margin_improvement': {
                'patterns': [
                    r'marginal.*?förbättrades.*?(\d+)',
                    r'lönsamhet.*?ökade.*?(\d+)',
                    r'margin.*?improved.*?(\d+)'
                ],
                'threshold': 2,  # 2%+ margin improvement
                'weight': 0.7
            },
            'large_contracts': {
                'patterns': [
                    r'kontrakt.*?värt.*?(\d+).*?(miljard|miljarder)',
                    r'order.*?(\d+).*?(miljard|miljarder)',
                    r'avtal.*?(\d+).*?(miljard|miljarder)'
                ],
                'threshold': 1,  # 1+ billion SEK
                'weight': 0.9
            },
            'market_share': {
                'patterns': [
                    r'marknadsandel.*?(\d+).*?procent',
                    r'market.*?share.*?(\d+).*?%'
                ],
                'threshold': 25,  # 25%+ market share is strong
                'weight': 0.6
            }
        }
        
        # 2. COMPETITIVE ADVANTAGE SIGNALS
        self.competitive_patterns = {
            'patents': [
                'patent', 'patentansökan', 'immaterialrätt', 'intellectual property',
                'teknisk genombrott', 'innovation', 'forskningsresultat'
            ],
            'regulatory_moat': [
                'regulatoriskt godkännande', 'licens', 'certifiering', 'FDA-godkännande',
                'CE-märkning', 'regulatory approval', 'compliance'
            ],
            'exclusive_deals': [
                'exklusiv', 'exclusive', 'ensamrätt', 'partnerskap', 'strategiskt samarbete'
            ],
            'barriers_to_entry': [
                'barriärer', 'svår att kopiera', 'unique', 'unik position', 'först i världen'
            ]
        }
        
        # 3. MANAGEMENT & GOVERNANCE SIGNALS
        self.management_patterns = {
            'insider_buying': [
                'vd köper aktier', 'ledning köper', 'insider buying', 'management köp'
            ],
            'leadership_change': [
                'ny vd', 'new ceo', 'ledningsbyte', 'management change'
            ],
            'strategic_vision': [
                'strategisk plan', 'vision', 'transformation', 'omstrukturering'
            ]
        }
        
        # 4. MARKET TIMING SIGNALS
        self.timing_patterns = {
            'earnings_surprise': [
                'överträffade förväntningarna', 'beat expectations', 'bättre än väntat'
            ],
            'guidance_raise': [
                'höjer prognos', 'raises guidance', 'uppjusterar', 'förbättrad prognos'
            ],
            'analyst_upgrades': [
                'uppgraderad', 'köpråd', 'buy rating', 'target price raised'
            ],
            'institutional_buying': [
                'institutionella investerare', 'institutional buying', 'fonder köper'
            ]
        }
        
        # 5. MACRO/SECTOR TAILWINDS
        self.tailwind_patterns = {
            'sector_rotation': [
                'sektorrotation', 'sector rotation', 'branschtrend'
            ],
            'regulatory_tailwinds': [
                'gynnsam reglering', 'regulatory support', 'statligt stöd'
            ],
            'demographic_trends': [
                'demografisk trend', 'aging population', 'urbanisering'
            ],
            'technology_adoption': [
                'teknisk adoption', 'digital transformation', 'AI adoption'
            ]
        }
        
        # 6. VALUE SIGNALS
        self.value_patterns = {
            'undervalued': [
                'undervärderad', 'undervalued', 'lågt värderad', 'rabatt'
            ],
            'asset_value': [
                'tillgångsvärde', 'asset value', 'bokfört värde', 'substansvärde'
            ],
            'cash_rich': [
                'kassarik', 'cash rich', 'stark balansräkning', 'skuldfri'
            ]
        }

    def analyze_advanced_signals(self, title: str, content: str, snippet: str) -> List[AdvancedSignal]:
        """Analyze article for advanced trading signals beyond sentiment."""
        signals = []
        full_text = f"{title} {content} {snippet}".lower()
        
        # 1. Quantitative Analysis
        quant_signals = self._analyze_quantitative(full_text)
        signals.extend(quant_signals)
        
        # 2. Competitive Advantage Analysis
        competitive_signals = self._analyze_competitive_advantage(full_text)
        signals.extend(competitive_signals)
        
        # 3. Management & Governance
        management_signals = self._analyze_management(full_text)
        signals.extend(management_signals)
        
        # 4. Market Timing
        timing_signals = self._analyze_timing(full_text)
        signals.extend(timing_signals)
        
        # 5. Macro Tailwinds
        tailwind_signals = self._analyze_tailwinds(full_text)
        signals.extend(tailwind_signals)
        
        # 6. Value Signals
        value_signals = self._analyze_value(full_text)
        signals.extend(value_signals)
        
        # 7. Risk Factors (negative signals)
        risk_signals = self._analyze_risks(full_text)
        signals.extend(risk_signals)
        
        return signals
    
    def _analyze_quantitative(self, text: str) -> List[AdvancedSignal]:
        """Analyze quantitative metrics."""
        signals = []
        
        for metric, config in self.quantitative_patterns.items():
            for pattern in config['patterns']:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        value = float(match.group(1))
                        if value >= config['threshold']:
                            strength = min(1.0, value / (config['threshold'] * 2))
                            signals.append(AdvancedSignal(
                                signal_type=f"quantitative_{metric}",
                                strength=strength * config['weight'],
                                explanation=f"{metric.replace('_', ' ').title()}: {value}%+ detected",
                                confidence=0.8,
                                timeframe="short-term"
                            ))
                    except (ValueError, IndexError):
                        continue
        
        return signals
    
    def _analyze_competitive_advantage(self, text: str) -> List[AdvancedSignal]:
        """Analyze competitive advantage indicators."""
        signals = []
        
        for advantage_type, keywords in self.competitive_patterns.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            if matches > 0:
                strength = min(1.0, matches / 3)  # Normalize to max 3 keywords
                signals.append(AdvancedSignal(
                    signal_type=f"competitive_{advantage_type}",
                    strength=strength * 0.7,
                    explanation=f"Competitive advantage: {advantage_type.replace('_', ' ')} indicators found",
                    confidence=0.6,
                    timeframe="long-term"
                ))
        
        return signals
    
    def _analyze_management(self, text: str) -> List[AdvancedSignal]:
        """Analyze management and governance signals."""
        signals = []
        
        for signal_type, keywords in self.management_patterns.items():
            if any(keyword in text for keyword in keywords):
                strength_map = {
                    'insider_buying': 0.8,
                    'leadership_change': 0.6,
                    'strategic_vision': 0.5
                }
                signals.append(AdvancedSignal(
                    signal_type=f"management_{signal_type}",
                    strength=strength_map.get(signal_type, 0.5),
                    explanation=f"Management signal: {signal_type.replace('_', ' ')}",
                    confidence=0.7,
                    timeframe="medium-term"
                ))
        
        return signals
    
    def _analyze_timing(self, text: str) -> List[AdvancedSignal]:
        """Analyze market timing signals."""
        signals = []
        
        for signal_type, keywords in self.timing_patterns.items():
            if any(keyword in text for keyword in keywords):
                strength_map = {
                    'earnings_surprise': 0.9,
                    'guidance_raise': 0.8,
                    'analyst_upgrades': 0.7,
                    'institutional_buying': 0.6
                }
                signals.append(AdvancedSignal(
                    signal_type=f"timing_{signal_type}",
                    strength=strength_map.get(signal_type, 0.5),
                    explanation=f"Timing signal: {signal_type.replace('_', ' ')}",
                    confidence=0.8,
                    timeframe="immediate"
                ))
        
        return signals
    
    def _analyze_tailwinds(self, text: str) -> List[AdvancedSignal]:
        """Analyze macro and sector tailwinds."""
        signals = []
        
        for tailwind_type, keywords in self.tailwind_patterns.items():
            if any(keyword in text for keyword in keywords):
                signals.append(AdvancedSignal(
                    signal_type=f"tailwind_{tailwind_type}",
                    strength=0.6,
                    explanation=f"Tailwind: {tailwind_type.replace('_', ' ')}",
                    confidence=0.5,
                    timeframe="long-term"
                ))
        
        return signals
    
    def _analyze_value(self, text: str) -> List[AdvancedSignal]:
        """Analyze value investing signals."""
        signals = []
        
        for value_type, keywords in self.value_patterns.items():
            if any(keyword in text for keyword in keywords):
                strength_map = {
                    'undervalued': 0.7,
                    'asset_value': 0.6,
                    'cash_rich': 0.8
                }
                signals.append(AdvancedSignal(
                    signal_type=f"value_{value_type}",
                    strength=strength_map.get(value_type, 0.5),
                    explanation=f"Value signal: {value_type.replace('_', ' ')}",
                    confidence=0.6,
                    timeframe="medium-term"
                ))
        
        return signals
    
    def _analyze_risks(self, text: str) -> List[AdvancedSignal]:
        """Analyze risk factors (negative signals)."""
        signals = []
        
        risk_keywords = [
            'varning', 'warning', 'förlust', 'loss', 'nedgång', 'decline',
            'konkurrens', 'competition', 'reglering', 'regulation threat',
            'skulder', 'debt', 'lawsuit', 'stämning', 'investigation'
        ]
        
        risk_count = sum(1 for keyword in risk_keywords if keyword in text)
        if risk_count > 0:
            signals.append(AdvancedSignal(
                signal_type="risk_factors",
                strength=-min(1.0, risk_count / 3),  # Negative signal
                explanation=f"Risk factors detected: {risk_count} indicators",
                confidence=0.7,
                timeframe="immediate"
            ))
        
        return signals
    
    def calculate_advanced_score(self, signals: List[AdvancedSignal]) -> Dict[str, float]:
        """Calculate overall advanced scoring."""
        if not signals:
            return {
                'advanced_score': 0.0,
                'confidence': 0.0,
                'signal_count': 0,
                'risk_adjusted_score': 0.0
            }
        
        # Calculate weighted score
        total_score = 0.0
        total_weight = 0.0
        risk_adjustment = 0.0
        
        for signal in signals:
            weight = signal.confidence
            if signal.strength < 0:  # Risk factor
                risk_adjustment += abs(signal.strength) * weight
            else:
                total_score += signal.strength * weight
                total_weight += weight
        
        if total_weight > 0:
            advanced_score = total_score / total_weight
        else:
            advanced_score = 0.0
        
        # Apply risk adjustment
        risk_adjusted_score = max(0.0, advanced_score - risk_adjustment)
        
        # Calculate overall confidence
        avg_confidence = sum(s.confidence for s in signals) / len(signals)
        
        return {
            'advanced_score': advanced_score,
            'confidence': avg_confidence,
            'signal_count': len(signals),
            'risk_adjusted_score': risk_adjusted_score,
            'risk_factors': risk_adjustment
        }
    
    def get_signal_summary(self, signals: List[AdvancedSignal]) -> str:
        """Get human-readable summary of signals."""
        if not signals:
            return "No advanced signals detected"
        
        # Group by type
        signal_groups = {}
        for signal in signals:
            category = signal.signal_type.split('_')[0]
            if category not in signal_groups:
                signal_groups[category] = []
            signal_groups[category].append(signal)
        
        summary_parts = []
        for category, group_signals in signal_groups.items():
            strong_signals = [s for s in group_signals if s.strength > 0.6]
            if strong_signals:
                summary_parts.append(f"{category.title()}({len(strong_signals)})")
        
        if summary_parts:
            return " | ".join(summary_parts)
        else:
            return "Weak signals detected"


# Global instance
advanced_analyzer = AdvancedAnalyzer()


def get_advanced_analyzer() -> AdvancedAnalyzer:
    """Get the global advanced analyzer instance."""
    return advanced_analyzer 