"""
Company mapping and ticker identification for the Morning Scanner application.

This module provides:
- Company name to stock ticker mapping
- Fuzzy matching for company names
- Ticker validation
- Company information lookup
"""

import csv
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
from rapidfuzz import fuzz


class CompanyMapper:
    """
    Maps company names to stock tickers using fuzzy matching.
    
    This class provides:
    - Exact and fuzzy matching of company names
    - Ticker validation
    - Company information lookup
    - Extensible mapping database
    """
    
    def __init__(self, tickers_file: Optional[str] = None):
        """
        Initialize the company mapper.
        
        Args:
            tickers_file (str, optional): Path to tickers CSV file
        """
        self.logger = logging.getLogger(__name__)
        
        # Default tickers file path
        if tickers_file is None:
            tickers_file = Path(__file__).parent / 'tickers.csv'
        
        self.tickers_file = Path(tickers_file)
        self.companies_df = None
        self.company_mapping = {}
        
        # Common company name variations
        self.name_variations = {
            'ericsson': ['ericsson', 'eric', 'telefonaktiebolaget l m ericsson'],
            'volvo': ['volvo', 'volvo group', 'ab volvo'],
            'h&m': ['h&m', 'h&m hennes & mauritz', 'hennes & mauritz'],
            'atlas copco': ['atlas copco', 'atlas', 'atlas copco group'],
            'sandvik': ['sandvik', 'sandvik group'],
            'seb': ['seb', 'skandinaviska enskilda banken', 'enskilda banken'],
            'swedbank': ['swedbank', 'swedbank group'],
            'handelsbanken': ['handelsbanken', 'svenska handelsbanken'],
            'skanska': ['skanska', 'skanska group'],
            'hexagon': ['hexagon', 'hexagon ab'],
            'essity': ['essity', 'essity ab'],
            'electrolux': ['electrolux', 'electrolux ab'],
            'assa abloy': ['assa abloy', 'assa', 'abloy'],
            'investor': ['investor', 'investor ab'],
            'stora enso': ['stora enso', 'stora', 'enso'],
            'svenska cellulosa': ['svenska cellulosa', 'sca', 'sca ab'],
            'telia': ['telia', 'telia company', 'telia sonera'],
            'tele2': ['tele2', 'tele2 ab']
        }
        
        # Load company data
        self._load_companies()
    
    def _load_companies(self):
        """Load company data from CSV file."""
        try:
            if self.tickers_file.exists():
                self.companies_df = pd.read_csv(self.tickers_file)
                self.logger.info(f"Loaded {len(self.companies_df)} companies from {self.tickers_file}")
                
                # Create reverse mapping for faster lookups
                for _, row in self.companies_df.iterrows():
                    company_name = row['Company Name'].lower().strip()
                    self.company_mapping[company_name] = row.to_dict()
                    
                    # Add variations
                    if company_name in self.name_variations:
                        for variation in self.name_variations[company_name]:
                            self.company_mapping[variation] = row.to_dict()
            else:
                self.logger.warning(f"Tickers file not found: {self.tickers_file}")
                self.companies_df = pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error loading companies: {str(e)}")
            self.companies_df = pd.DataFrame()
    
    def map_company(self, text: str, threshold: float = 0.8) -> Optional[Dict]:
        """
        Map company name in text to ticker information.
        
        Args:
            text (str): Text containing potential company names
            threshold (float): Minimum similarity threshold for fuzzy matching
            
        Returns:
            Dict or None: Company information if found, None otherwise
        """
        if not text or not self.company_mapping:
            return None
        
        # Clean and normalize text
        text = self._clean_text(text.lower())
        
        # Try exact match first
        exact_match = self._exact_match(text)
        if exact_match:
            return exact_match
        
        # Try partial matches
        partial_match = self._partial_match(text)
        if partial_match:
            return partial_match
        
        # Try fuzzy matching
        fuzzy_match = self._fuzzy_match(text, threshold)
        if fuzzy_match:
            return fuzzy_match
        
        return None
    
    def _exact_match(self, text: str) -> Optional[Dict]:
        """
        Try to find exact matches for company names.
        
        Args:
            text (str): Normalized text to search
            
        Returns:
            Dict or None: Company information if exact match found
        """
        # Check for exact matches in company mapping
        for company_name, company_info in self.company_mapping.items():
            if company_name in text:
                self.logger.debug(f"Exact match found: {company_name}")
                return company_info
        
        return None
    
    def _partial_match(self, text: str) -> Optional[Dict]:
        """
        Try to find partial matches for company names.
        
        Args:
            text (str): Normalized text to search
            
        Returns:
            Dict or None: Company information if partial match found
        """
        # Split text into words and check for company name parts
        words = text.split()
        
        for company_name, company_info in self.company_mapping.items():
            company_words = company_name.split()
            
            # Check if all company words are present in text
            if all(word in words for word in company_words):
                self.logger.debug(f"Partial match found: {company_name}")
                return company_info
        
        return None
    
    def _fuzzy_match(self, text: str, threshold: float) -> Optional[Dict]:
        """
        Try to find fuzzy matches for company names.
        
        Args:
            text (str): Normalized text to search
            threshold (float): Minimum similarity threshold
            
        Returns:
            Dict or None: Company information if fuzzy match found
        """
        best_match = None
        best_score = 0
        
        for company_name, company_info in self.company_mapping.items():
            # Calculate similarity scores using different methods
            ratio_score = fuzz.ratio(text, company_name) / 100.0
            partial_score = fuzz.partial_ratio(text, company_name) / 100.0
            token_sort_score = fuzz.token_sort_ratio(text, company_name) / 100.0
            
            # Use the best score
            score = max(ratio_score, partial_score, token_sort_score)
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = company_info
        
        if best_match:
            self.logger.debug(f"Fuzzy match found with score {best_score:.2f}")
        
        return best_match
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text for matching.
        
        Args:
            text (str): Raw text to clean
            
        Returns:
            str: Cleaned and normalized text
        """
        if not text:
            return ""
        
        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text.strip())
        
        return text
    
    def get_company_info(self, ticker: str) -> Optional[Dict]:
        """
        Get company information by ticker.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            Dict or None: Company information if found
        """
        if self.companies_df is not None:
            match = self.companies_df[self.companies_df['Ticker'] == ticker]
            if not match.empty:
                return match.iloc[0].to_dict()
        
        return None
    
    def search_companies(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for companies by name or ticker.
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results
            
        Returns:
            List[Dict]: List of matching companies
        """
        if self.companies_df is None:
            return []
        
        query = query.lower()
        results = []
        
        for _, row in self.companies_df.iterrows():
            company_name = row['Company Name'].lower()
            ticker = row['Ticker'].lower()
            
            if query in company_name or query in ticker:
                results.append(row.to_dict())
                
                if len(results) >= limit:
                    break
        
        return results
    
    def add_company(self, company_name: str, ticker: str, exchange: str = 'STO', 
                    country: str = 'Sweden', sector: str = 'Unknown'):
        """
        Add a new company to the mapping.
        
        Args:
            company_name (str): Company name
            ticker (str): Stock ticker
            exchange (str): Stock exchange
            country (str): Country
            sector (str): Business sector
        """
        new_company = {
            'Company Name': company_name,
            'Ticker': ticker,
            'Exchange': exchange,
            'Country': country,
            'Sector': sector
        }
        
        # Add to DataFrame
        if self.companies_df is not None:
            self.companies_df = pd.concat([self.companies_df, pd.DataFrame([new_company])], ignore_index=True)
        
        # Add to mapping
        company_name_lower = company_name.lower().strip()
        self.company_mapping[company_name_lower] = new_company
        
        self.logger.info(f"Added company: {company_name} ({ticker})")
    
    def save_companies(self, file_path: Optional[str] = None):
        """
        Save company data to CSV file.
        
        Args:
            file_path (str, optional): Path to save file. If None, uses default location.
        """
        if self.companies_df is None:
            self.logger.warning("No company data to save")
            return
        
        try:
            save_path = Path(file_path) if file_path else self.tickers_file
            self.companies_df.to_csv(save_path, index=False)
            self.logger.info(f"Saved {len(self.companies_df)} companies to {save_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving companies: {str(e)}")
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the company mapping.
        
        Returns:
            Dict: Mapping statistics
        """
        if self.companies_df is None:
            return {'total_companies': 0, 'exchanges': [], 'sectors': []}
        
        return {
            'total_companies': len(self.companies_df),
            'exchanges': self.companies_df['Exchange'].unique().tolist(),
            'sectors': self.companies_df['Sector'].unique().tolist()
        } 