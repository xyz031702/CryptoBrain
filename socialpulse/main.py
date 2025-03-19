"""Main entry point for SocialPulse."""

import sys
import os
import argparse
from typing import List

import sys
import os

# Add module directories to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from social_connectors.x_connector import XConnector
from core.trend_analyzer import TrendAnalyzer
from models.trend import TrendTopic

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="SocialPulse - Social media analysis for crypto trends"
    )
    parser.add_argument(
        "--keywords", 
        nargs="+", 
        default=["crypto", "bitcoin", "ethereum", "blockchain", "nft", "defi"],
        help="Keywords to filter trending topics"
    )
    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_args()
    
    # Create connectors (only X for now)
    x_connector = XConnector()
    connectors = [x_connector]
    
    # Create trend analyzer
    analyzer = TrendAnalyzer(connectors)
    
    # Get trends
    print(f"Getting trends for keywords: {', '.join(args.keywords)}")
    trends = analyzer.get_trends(args.keywords)
    
    # Display trends
    if trends:
        print(f"\nFound {len(trends)} trending topics:")
        for i, trend in enumerate(trends, 1):
            volume = f"{trend.volume:,d} tweets" if trend.volume else "unknown volume"
            print(f"{i}. {trend.name} ({volume}) [Platform: {trend.platform}]")
        
        # Display trend analysis
        analysis = analyzer.analyze_trend_volume(trends)
        print(f"\nTrend Analysis:")
        print(f"Total Volume: {analysis['total_volume']:,d} tweets")
        print(f"Average Volume: {analysis['average_volume']:,.2f} tweets per trend")
    else:
        print("No trends found matching the specified keywords.")

if __name__ == "__main__":
    main()
