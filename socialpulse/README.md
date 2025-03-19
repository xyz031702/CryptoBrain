# SocialPulse (Simplified)

A simplified version of the SocialPulse module focusing on core functionality for cryptocurrency trend analysis on social media platforms.

## Simplified Structure

```
simplified_socialpulse/
├── __init__.py                 # Package initialization
├── exceptions.py               # Custom exceptions
├── main.py                     # Main entry point
├── setup.py                    # Installation script
│
├── core/                       # Core functionality
│   ├── __init__.py
│   └── trend_analyzer.py       # Trend analysis engine
│
├── models/                     # Data models
│   ├── __init__.py
│   └── trend.py                # Trend model
│
├── social_connectors/          # Social media connectors
│   ├── __init__.py             # Base connector interfaces
│   └── x_connector.py          # X (Twitter) connector
│
└── utils/                      # Utility functions
    └── __init__.py
```

## Installation & Usage

### Installation

```bash
pip install -e .
```

### Usage

```python
from simplified_socialpulse.social_connectors.x_connector import XConnector
from simplified_socialpulse.core.trend_analyzer import TrendAnalyzer

# Create X connector
x_connector = XConnector()

# Create analyzer with connectors
analyzer = TrendAnalyzer([x_connector])

# Get and analyze crypto-related trends
trends = analyzer.get_trends(keywords=["crypto", "bitcoin", "ethereum"])

# Display trends
for trend in trends:
    print(f"{trend.name} - {trend.volume} tweets")

# Get volume analysis
analysis = analyzer.analyze_trend_volume(trends)
print(f"Total volume: {analysis['total_volume']} tweets")
```

## Command Line Interface

```bash
python -m simplified_socialpulse.main --keywords crypto bitcoin ethereum
```

## Future Development

This simplified version focuses on the core functionality. Future development will include:

1. Additional social media connectors (Reddit, Discord, etc.)
2. Content generation capabilities
3. Sentiment analysis
4. Database integration for trend persistence
5. API endpoints for integration
6. Visualization and reporting
