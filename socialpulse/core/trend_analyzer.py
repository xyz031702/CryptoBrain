"""Core trend analysis functionality."""

from typing import List, Dict, Optional
from datetime import datetime

import sys
import os

# Add parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from social_connectors import BaseSocialConnector
from models.trend import TrendTopic

class TrendAnalyzer:
    """Analyzes trend data from various social platforms."""
    
    def __init__(self, connectors: List[BaseSocialConnector]):
        """
        Initialize trend analyzer with social connectors.
        
        Args:
            connectors: List of social media connectors
        """
        self.connectors = connectors
    
    def get_trends(self, keywords: List[str]) -> List[TrendTopic]:
        """
        Get trending topics from all connected platforms.
        
        Args:
            keywords: List of keywords to filter trending topics
            
        Returns:
            List of TrendTopic objects
        """
        all_trends = []
        
        for connector in self.connectors:
            try:
                # Get platform name from connector class
                platform_name = connector.__class__.__name__.replace("Connector", "").lower()
                
                # Get trending topics
                raw_trends = connector.get_trending_topics(keywords=keywords)
                
                # Convert to TrendTopic objects
                for trend in raw_trends:
                    if platform_name == "x":
                        trend_topic = TrendTopic.from_x_data(trend)
                    else:
                        # Generic conversion for other platforms
                        trend_topic = TrendTopic(
                            name=trend.get("name", "Unknown trend"),
                            volume=trend.get("volume"),
                            platform=platform_name,
                            metadata=trend
                        )
                    all_trends.append(trend_topic)
                    
            except Exception as e:
                print(f"Error getting trends from {connector.__class__.__name__}: {str(e)}")
                
        return all_trends
    
    def analyze_trend_volume(self, trends: List[TrendTopic]) -> Dict:
        """
        Analyze trend volume data.
        
        Args:
            trends: List of TrendTopic objects
            
        Returns:
            Dictionary with trend volume analysis
        """
        if not trends:
            return {"error": "No trends to analyze"}
        
        # Sort trends by volume (descending)
        sorted_trends = sorted(
            [t for t in trends if t.volume is not None], 
            key=lambda x: x.volume, 
            reverse=True
        )
        
        # Get top trends
        top_trends = sorted_trends[:5] if len(sorted_trends) >= 5 else sorted_trends
        
        # Calculate total volume
        total_volume = sum(t.volume for t in trends if t.volume is not None)
        
        # Calculate average volume
        avg_volume = total_volume / len([t for t in trends if t.volume is not None]) if total_volume > 0 else 0
        
        return {
            "total_trends": len(trends),
            "total_volume": total_volume,
            "average_volume": avg_volume,
            "top_trends": [t.to_dict() for t in top_trends],
            "timestamp": datetime.now().isoformat()
        }
