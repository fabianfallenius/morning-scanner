# Morning Scanner

A Python-based financial news scanner that aggregates and ranks market-relevant information from various Swedish financial sources. Designed to provide a comprehensive morning briefing without automated trading capabilities.

## What It Does

Morning Scanner monitors multiple financial news sources (MFN, DI Morgonkoll, and others) to:
- Collect publicly available news metadata (titles, links, snippets, timestamps)
- Analyze content using NLP techniques to identify market-relevant keywords
- Map companies to their stock tickers
- Rank news items by relevance and importance
- Output a curated, ranked list for manual review

## Features

- **Respectful Scraping**: Only accesses publicly visible metadata, respects robots.txt
- **Stockholm Timezone**: All timestamps and scheduling in Europe/Stockholm time
- **No Auto-Trading**: Outputs ranked lists for manual decision-making only
- **Beginner-Friendly**: Well-commented, simple code structure
- **Multiple Output Formats**: Email and Telegram delivery options

## Quick Start

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Local Setup
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd morning-scanner
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy environment template and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

5. Run the scanner:
   ```bash
   python main.py
   ```

### Scheduled Execution

#### Using cron (Linux/macOS)
```bash
# Add to crontab (crontab -e)
0 7 * * 1-5 cd /path/to/morning-scanner && /path/to/venv/bin/python main.py
```

#### Using Task Scheduler (Windows)
- Open Task Scheduler
- Create Basic Task
- Set trigger to daily at 7:00 AM
- Action: Start a program
- Program: `python.exe`
- Arguments: `main.py`
- Start in: `C:\path\to\morning-scanner`

## Configuration

Edit `.env` file to configure:
- API keys for news sources
- Email/Telegram credentials
- Database connections
- Logging levels
- Timezone settings

## Safety & Terms of Service

### Important Notes
- **No Automated Trading**: This tool is for information gathering only
- **Respectful Scraping**: Only accesses publicly available metadata
- **Rate Limiting**: Built-in delays to avoid overwhelming source servers
- **Terms Compliance**: Check each source's ToS before use

### Legal Considerations
- Verify compliance with each news source's terms of service
- Respect robots.txt files and rate limiting
- Use only for personal, non-commercial purposes
- Consider data retention policies and GDPR compliance

## Project Structure

```
morning-scanner/
├── common/           # Shared utilities and configuration
├── sources/          # News source scrapers
├── mapping/          # Company-ticker mapping
├── nlp/             # Natural language processing
├── rank/            # News ranking algorithms
├── output/          # Output formatters and senders
├── storage/         # Data storage and logging
└── scripts/         # Utility scripts
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with clear comments
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and personal use only. Please respect the terms of service of all external data sources.

## Support

For issues and questions:
- Check the logs in `storage/errors.log`
- Review the configuration in `.env`
- Ensure all dependencies are properly installed 