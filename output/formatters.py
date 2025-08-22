"""Format news reports for output."""

from typing import List, Dict
from datetime import datetime

class ReportFormatter:
    """Format news items into readable reports."""
    
    def format(self, ranked_news: List[Dict]) -> str:
        """Format ranked news into a readable report."""
        if not ranked_news:
            return "No news items to report."
        
        report_lines = []
        report_lines.append("=== MORNING MARKET SCANNER REPORT ===")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Total items: {len(ranked_news)}")
        report_lines.append("")
        
        for item in ranked_news[:10]:  # Top 10 items
            rank = item.get('rank', 'N/A')
            title = item.get('title', 'No title')
            source = item.get('source', 'Unknown')
            relevance = item.get('classification', {}).get('relevance_score', 0.0)
            
            report_lines.append(f"{rank}. {title}")
            report_lines.append(f"   Source: {source} | Relevance: {relevance:.2f}")
            report_lines.append("")
        
        return "\n".join(report_lines) 