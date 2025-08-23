"""
Keyword extraction and analysis for Swedish financial news.

This module provides:
- Swedish financial keywords for positive/negative sentiment
- Catalyst event identification
- Keyword scoring and relevance calculation
- Industry-specific keyword categories
"""

import logging
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class KeywordMatch:
    """Represents a keyword match in text."""
    keyword: str
    category: str
    position: int
    context: str
    score: float


class SwedishFinancialKeywords:
    """
    Swedish financial keywords for news analysis.
    
    This class provides comprehensive keyword sets for:
    - Positive financial events
    - Negative financial events  
    - Catalyst events
    - Industry-specific terms
    """
    
    def __init__(self):
        """Initialize with Swedish financial keywords."""
        self.logger = logging.getLogger(__name__)
        
        # Positive financial keywords
        self.POSITIVE_KEYWORDS = [
            "resultatlyft", "vinstlyft", "marginallyft", "stark rapport", "överträffar förväntningarna", "bättre än väntat",
            "bättre än prognos", "höjer prognos", "höjer guidning", "guidning över väntan", "höjer utsikter", "starkare utsikter",
            "stark orderingång", "rekordorderingång", "rekordorder", "stororder", "miljardorder", "betydande order", "flerårigt avtal",
            "ramavtal", "förlängt avtal", "ny kund", "stor kund", "strategiskt avtal", "strategiskt partnerskap", "samarbete", "joint venture",
            "exklusivt avtal", "licensavtal", "distributionsavtal", "lanserar", "produktlansering", "marknadslansering", "kommersialisering",
            "kommersiellt genombrott", "genombrottsorder", "regulatoriskt godkännande", "godkännande", "godkänd", "CE-märkning", "CE-märke",
            "FDA-godkännande", "marknadsgodkännande", "patent beviljat", "patentportfölj stärks", "indexinträde", "tas in i index",
            "inkluderas i index", "återinförs i index", "IPO klar", "noteras på First North", "notering godkänd", "uppgraderas", "uppgradering",
            "höjd rekommendation", "höjd riktkurs", "köpråd", "stark köprekommendation", "höjer riktkurs", "övervikt", "outperform",
            "överträffar guidning", "överträffar estimat", "höjer utdelning", "extrautdelning", "återköp", "aktieåterköp",
            "omvänd vinstvarning", "preliminärt över förväntan", "stark inledning av året", "stark avslutning", "växer snabbare än marknaden",
            "stark organisk tillväxt", "rekordförsäljning", "rekordomsättning", "rekordvinst", "vänder till vinst", "tillbaka till vinst",
            "lönsamhet förbättras", "bruttomarginal upp", "rörelsemarginal upp", "kassaflöde förbättras", "skuldsättning minskar",
            "soliditet förbättras", "mål uppnås i förtid", "överträffar finansiella mål", "höjer finansiella mål", "upprepar stark guidning",
            "ny marknad", "expansion", "etablerar sig i", "vinner upphandling", "viktig upphandling", "upphandlingsseger", "stor leverans",
            "uppskalning", "kapacitet utökas", "produktionsökning", "investering i kapacitet", "fabrik byggs", "orderbok växer",
            "stark efterfrågan", "övertecknad emission", "insiderköp", "vd köper aktier", "ledning ökar innehav", "storägares köp",
            "ankarinvesterare", "positivt besked", "positiv nyhet", "positiv kursreaktion", "stark öppning väntas", "stark morgon",
            "uppåt på börsen", "starkt sentiment", "riskaptit ökar", "stark sektorutveckling", "vinner marknadsandelar", "lyckad pilot",
            "lyckat test", "valideringsdata positiva", "klinisk framgång", "fas 2 lyckas", "fas 3 lyckas", "myndighetsgodkännande",
            "intäktsdelning", "royaltyintäkter", "exklusivitetsperiod", "prisjustering upp", "prishöjning", "stark orderpipeline",
            "backlog växer", "lönsam tillväxt", "höjer långsiktiga mål", "delägare", "bekräftat"
        ]
        
        # Catalyst event keywords
        self.CATALYST_KEYWORDS = [
            "bevakningsstart", "bevakning inledd", "initierar bevakning", "höjd bevakning", "konferenscall", "kapitalmarknadsdag", "CMD",
            "kapitalmarknadsuppdatering", "produktuppdatering", "uppdaterar marknaden", "trading update", "månadsrapport", "försäljningssiffror",
            "trafiksiffror", "kundtillväxt", "abonnenttillväxt", "bokslut", "delårsrapport", "Q1", "Q2", "Q3", "Q4", "preliminär rapport",
            "årsredovisning", "guidance upprepas", "outlook upprepas", "affärsuppgörelse", "LOI", "letter of intent", "MOU", "avsiktsförklaring",
            "strategisk översyn", "avknoppning", "spin-off", "särnotering", "listbyte", "flytt till huvudlista", "stigande ägarandel", "ny styrelseledamot",
            "ny vd", "ny CFO", "ägarförändring", "flaggning", "flaggar upp", "flaggar över tröskel", "ökat institutionsintresse", "täcker emissionsbehov",
            "säkrar finansiering", "grönt ljus", "tilldelning klar", "lyckad book-building", "positiva förhandsbokningar", "förhandsintresse starkt",
            "exportorder", "marknadspenetration", "återstart", "produktionsstart", "produktionsåterupptag", "leveranser återupptas",
            "legala hinder undanröjda", "tvist löst", "skiljedom positiv", "skattefråga löst", "godkänd ansökan", "tillstånd beviljat",
            "miljötillstånd klart", "nätverksavtal", "operatörsavtal", "återförsäljarnät växer", "certifiering klar", "kvalitetsmärkning",
            "pilotkund", "referenskund", "lyckad POC", "proof of concept", "förbättrad visibilitet", "orderingång framåtblick", "pipeline indikatorer",
            "sektorn i fokus", "tematisk medvind"
        ]
        
        # Negative financial keywords
        self.NEGATIVE_KEYWORDS = [
            "vinstvarning", "sänker prognos", "sänker guidning", "prognos under väntan", "lägre än väntat", "svag rapport",
            "missar förväntningarna", "svag orderingång", "ordertapp", "förlorar upphandling", "tappar kund", "avslutar avtal",
            "samarbetet avslutas", "försenad lansering", "försening", "leveransproblem", "produktionsstopp", "produktionsproblem",
            "flaskhalsar", "kapacitetsbrist", "komponentbrist", "kvalitetsproblem", "återkallelse", "återkallar produkt",
            "regulatorisk försening", "regulatoriskt avslag", "avslag", "FDA-brev", "varningsbrev", "CE-problem", "säkerhetsbrister",
            "data otillräckliga", "studie misslyckas", "negativt utfall", "negativ studie", "utredning", "granskning", "tillsyn",
            "myndighetsprövning", "rättsprocess", "stämning", "dom mot bolaget", "sanktionsrisk", "cyberattack", "dataintrång",
            "bedrägeriutredning", "negativ press", "miljöböter", "tvist", "leverantörsproblem", "kundförlust", "prispress", "marginalpress",
            "bruttomarginal ner", "rörelsemarginal ner", "lönsamhet försämras", "kassaflöde försvagas", "skuldsättning ökar", "covenant-risk",
            "refinansieringsrisk", "kreditfacilitet sägs upp", "räntenetto pressas", "svag efterfrågan", "lagerökning", "försäljningsnedgång",
            "avyttrar till reapris", "nedskrivning", "impairment", "goodwillnedskrivning", "varulagernedskrivning", "VD avgår", "CFO avgår",
            "ledningsavhopp", "styrelsekris", "ägarkonflikt", "negativt besked", "negativ kursreaktion", "sänkt rekommendation", "sänkt riktkurs",
            "säljråd", "undervikt", "underperform", "handelsstopp", "handelsstoppas", "observationslista", "granskning av börsen",
            "företrädesemission", "nyemission", "riktad emission", "utspädning", "konvertibler", "teckningsoptioner", "likviditetsbrist",
            "going concern-varning", "konkursansökan", "företagsrekonstruktion", "rekonstruktion", "kontrollbalansräkning", "förlorar indexplats",
            "lämnar index"
        ]
        
        # Industry-specific keywords
        self.INDUSTRY_KEYWORDS = {
            'tech': ['AI', 'maskininlärning', 'blockchain', 'cloud', 'cybersäkerhet', 'digitalisering', 'IoT', '5G', 'edge computing'],
            'healthcare': ['läkemedel', 'klinisk studie', 'FDA', 'CE-märkning', 'terapi', 'diagnostik', 'medicinteknik', 'biotech'],
            'finance': ['bank', 'försäkring', 'kapitalförvaltning', 'kredit', 'hypotek', 'investering', 'trading', 'fintech'],
            'energy': ['solenergi', 'vindkraft', 'batterier', 'elektriska fordon', 'grön energi', 'hållbarhet', 'klimat', 'CO2'],
            'real_estate': ['fastighet', 'byggande', 'infrastruktur', 'logistik', 'kontor', 'bostäder', 'hyresfastighet', 'utveckling']
        }
        
        # Swedish companies (major stocks)
        self.SWEDISH_COMPANIES = [
            'ericsson', 'volvo', 'atlas copco', 'seb', 'handelsbanken', 'nordea',
            'ssab', 'sandvik', 'skf', 'hexagon', 'getinge', 'essity', 'hemtex',
            'clas ohlson', 'bilia', 'volvo cars', 'kinnevik', 'investor',
            'astrazeneca', 'ericsson b', 'volvo b', 'atlas copco b', 'seb a',
            'handelsbanken a', 'nordea bank', 'ssab a', 'sandvik a', 'skf b',
            'hexagon b', 'getinge b', 'essity b', 'hemtex b', 'clas ohlson b',
            'bilia b', 'kinnevik b', 'investor b',
        ]
        
        # Swedish financial terms
        self.SWEDISH_FINANCIAL_TERMS = [
            'omx', 'stockholm', 'börs', 'aktie', 'aktier', 'utdelning', 'vinst',
            'tillväxt', 'omsättning', 'resultat', 'rapport', 'bokslut',
            'omx30', 'omx stockholm', 'stockholm börs', 'aktiebolag', 'utdelning',
            'vinstökning', 'tillväxt', 'omsättningsökning', 'resultatförbättring',
        ]
        
        # Swedish business terms
        self.SWEDISH_BUSINESS_TERMS = [
            'företag', 'bolag', 'koncern', 'fusion', 'uppköp', 'strategi',
            'investering', 'expansion', 'marknad', 'konkurrens', 'affärsområde',
            'affärsstrategi', 'affärsmodell', 'affärsutveckling', 'affärspartnerskap',
        ]
        
        # Create regex patterns for faster matching
        self._compile_patterns()
        
        self.logger.info(f"Initialized Swedish Financial Keywords: {len(self.POSITIVE_KEYWORDS)} positive, "
                        f"{len(self.NEGATIVE_KEYWORDS)} negative, {len(self.CATALYST_KEYWORDS)} catalyst")
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient keyword matching."""
        # Create word boundary patterns for exact word matching
        self.positive_pattern = re.compile(r'\b(' + '|'.join(map(re.escape, self.POSITIVE_KEYWORDS)) + r')\b', re.IGNORECASE)
        self.negative_pattern = re.compile(r'\b(' + '|'.join(map(re.escape, self.NEGATIVE_KEYWORDS)) + r')\b', re.IGNORECASE)
        self.catalyst_pattern = re.compile(r'\b(' + '|'.join(map(re.escape, self.CATALYST_KEYWORDS)) + r')\b', re.IGNORECASE)
    
    def extract_keywords(self, text: str) -> Dict[str, List[KeywordMatch]]:
        """
        Extract all keywords from text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict[str, List[KeywordMatch]]: Keywords organized by category
        """
        if not text:
            return {'positive': [], 'negative': [], 'catalyst': []}
        
        text_lower = text.lower()
        
        results = {
            'positive': self._find_keywords(text_lower, self.POSITIVE_KEYWORDS, 'positive'),
            'negative': self._find_keywords(text_lower, self.NEGATIVE_KEYWORDS, 'negative'),
            'catalyst': self._find_keywords(text_lower, self.CATALYST_KEYWORDS, 'catalyst')
        }
        
        return results
    
    def _find_keywords(self, text: str, keywords: List[str], category: str) -> List[KeywordMatch]:
        """
        Find keywords in text with context.
        
        Args:
            text (str): Lowercase text to search
            keywords (List[str]): Keywords to find
            category (str): Category of keywords
            
        Returns:
            List[KeywordMatch]: List of keyword matches
        """
        matches = []
        
        for keyword in keywords:
            if keyword.lower() in text:
                # Find all occurrences
                start = 0
                while True:
                    pos = text.find(keyword.lower(), start)
                    if pos == -1:
                        break
                    
                    # Extract context (50 characters before and after)
                    context_start = max(0, pos - 50)
                    context_end = min(len(text), pos + len(keyword) + 50)
                    context = text[context_start:context_end]
                    
                    # Calculate relevance score based on position and frequency
                    score = self._calculate_keyword_score(keyword, pos, len(text))
                    
                    match = KeywordMatch(
                        keyword=keyword,
                        category=category,
                        position=pos,
                        context=context,
                        score=score
                    )
                    matches.append(match)
                    
                    start = pos + 1
        
        return matches
    
    def _calculate_keyword_score(self, keyword: str, position: int, text_length: int) -> float:
        """
        Calculate relevance score for a keyword match.
        
        Args:
            keyword (str): The matched keyword
            position (int): Position in text
            text_length (int): Total text length
            
        Returns:
            float: Relevance score (0.0 to 1.0)
        """
        # Base score starts at 0.5
        score = 0.5
        
        # Position bonus: keywords at beginning get higher score
        if position < text_length * 0.1:  # First 10%
            score += 0.3
        elif position < text_length * 0.3:  # First 30%
            score += 0.2
        
        # Length bonus: longer keywords get higher score
        if len(keyword) > 20:
            score += 0.2
        elif len(keyword) > 10:
            score += 0.1
        
        # Category bonus: catalyst events get higher score
        if keyword in self.CATALYST_KEYWORDS:
            score += 0.1
        
        return min(1.0, score)
    
    def extract_positive_keywords(self, title: str, content: str = "", snippet: str = "") -> List[KeywordMatch]:
        """Extract positive keywords from text components."""
        full_text = f"{title} {content} {snippet}".strip()
        keywords = self.extract_keywords(full_text)
        return keywords.get('positive', [])
    
    def extract_negative_keywords(self, title: str, content: str = "", snippet: str = "") -> List[KeywordMatch]:
        """Extract negative keywords from text components."""
        full_text = f"{title} {content} {snippet}".strip()
        keywords = self.extract_keywords(full_text)
        return keywords.get('negative', [])
    
    def extract_catalyst_keywords(self, title: str, content: str = "", snippet: str = "") -> List[KeywordMatch]:
        """Extract catalyst keywords from text components."""
        full_text = f"{title} {content} {snippet}".strip()
        keywords = self.extract_keywords(full_text)
        return keywords.get('catalyst', [])
    
    def calculate_sentiment_score(self, positive_keywords: List[KeywordMatch], 
                                negative_keywords: List[KeywordMatch]) -> float:
        """Calculate sentiment score from keyword lists."""
        positive_score = sum(match.score for match in positive_keywords)
        negative_score = sum(match.score for match in negative_keywords)
        return positive_score - negative_score
    
    def calculate_relevance_score(self, positive_keywords: List[KeywordMatch],
                                negative_keywords: List[KeywordMatch],
                                catalyst_keywords: List[KeywordMatch]) -> float:
        """Calculate relevance score from keyword lists."""
        total_keywords = len(positive_keywords) + len(negative_keywords) + len(catalyst_keywords)
        total_score = (sum(match.score for match in positive_keywords) + 
                      sum(match.score for match in negative_keywords) +
                      sum(match.score for match in catalyst_keywords))
        
        # Basic relevance calculation
        if total_keywords == 0:
            return 0.0
        
        # Average keyword strength with bonus for quantity
        avg_strength = total_score / total_keywords
        quantity_bonus = min(0.3, total_keywords * 0.05)
        catalyst_bonus = min(0.2, len(catalyst_keywords) * 0.1)
        
        return min(1.0, avg_strength + quantity_bonus + catalyst_bonus)
    
    def classify_categories(self, positive_keywords: List[KeywordMatch],
                          catalyst_keywords: List[KeywordMatch]) -> List[str]:
        """Classify categories from keyword matches."""
        categories = set()
        
        # Extract categories from keyword matches
        for keyword_match in positive_keywords + catalyst_keywords:
            # Map keywords to categories based on patterns
            keyword_lower = keyword_match.keyword.lower()
            
            if any(word in keyword_lower for word in ['resultat', 'vinst', 'förlust', 'rapport', 'bokslut']):
                categories.add('earnings')
            elif any(word in keyword_lower for word in ['order', 'kontrakt', 'avtal', 'leverans']):
                categories.add('orders')
            elif any(word in keyword_lower for word in ['prognos', 'guidning', 'utskter', 'mål']):
                categories.add('guidance')
            elif any(word in keyword_lower for word in ['godkännande', 'regulatorisk', 'tillstånd']):
                categories.add('regulatory')
            elif any(word in keyword_lower for word in ['börs', 'handel', 'kurs', 'index']):
                categories.add('market')
            elif any(word in keyword_lower for word in ['emission', 'finansiering', 'lån', 'kredit']):
                categories.add('financial')
            elif any(word in keyword_lower for word in ['sektor', 'bransch', 'trend']):
                categories.add('industry')
        
        return list(categories)
    
    def get_keyword_summary(self, text: str) -> Dict[str, any]:
        """
        Get comprehensive keyword analysis summary.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict: Summary with counts, sentiment, and top keywords
        """
        keywords = self.extract_keywords(text)
        
        # Count keywords by category
        counts = {
            'positive': len(keywords['positive']),
            'negative': len(keywords['negative']),
            'catalyst': len(keywords['catalyst']),
            'total': len(keywords['positive']) + len(keywords['negative']) + len(keywords['catalyst'])
        }
        
        # Get top keywords by score
        top_positive = sorted(keywords['positive'], key=lambda x: x.score, reverse=True)[:5]
        top_negative = sorted(keywords['negative'], key=lambda x: x.score, reverse=True)[:5]
        top_catalyst = sorted(keywords['catalyst'], key=lambda x: x.score, reverse=True)[:5]
        
        # Calculate sentiment
        sentiment_score = self.calculate_sentiment_score(text)
        
        return {
            'counts': counts,
            'sentiment_score': sentiment_score,
            'sentiment_label': self._get_sentiment_label(sentiment_score),
            'top_positive': [{'keyword': m.keyword, 'score': m.score} for m in top_positive],
            'top_negative': [{'keyword': m.keyword, 'score': m.score} for m in top_negative],
            'top_catalyst': [{'keyword': m.keyword, 'score': m.score} for m in top_catalyst],
            'has_catalyst': counts['catalyst'] > 0,
            'overall_tone': 'positive' if sentiment_score > 0.1 else 'negative' if sentiment_score < -0.1 else 'neutral'
        }
    
    def _get_sentiment_label(self, score: float) -> str:
        """Convert sentiment score to human-readable label."""
        if score >= 0.5:
            return "Very Positive"
        elif score >= 0.1:
            return "Positive"
        elif score <= -0.5:
            return "Very Negative"
        elif score <= -0.1:
            return "Negative"
        else:
            return "Neutral"
    
    def is_high_impact_news(self, text: str) -> bool:
        """
        Determine if text contains high-impact financial news.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            bool: True if high-impact news detected
        """
        keywords = self.extract_keywords(text)
        
        # High impact if:
        # 1. High sentiment score (positive or negative)
        # 2. Contains catalyst keywords
        # 3. Multiple strong keywords
        
        sentiment_score = abs(self.calculate_sentiment_score(text))
        has_catalyst = len(keywords['catalyst']) > 0
        strong_keywords = len(keywords['positive']) + len(keywords['negative']) >= 3
        
        return sentiment_score > 0.3 or has_catalyst or strong_keywords
    
    def get_industry_relevance(self, text: str) -> Dict[str, float]:
        """
        Calculate relevance to different industries.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict[str, float]: Industry relevance scores
        """
        text_lower = text.lower()
        industry_scores = {}
        
        for industry, keywords in self.INDUSTRY_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1
            
            # Normalize score
            if keywords:
                industry_scores[industry] = min(1.0, score / len(keywords))
            else:
                industry_scores[industry] = 0.0
        
        return industry_scores


# Global instance for easy access
swedish_keywords = SwedishFinancialKeywords()


def get_keyword_analyzer() -> SwedishFinancialKeywords:
    """
    Get the global Swedish financial keywords analyzer.
    
    Returns:
        SwedishFinancialKeywords: Keyword analyzer instance
    """
    return swedish_keywords 