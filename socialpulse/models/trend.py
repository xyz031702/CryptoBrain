"""Trend model for social media topics."""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class TrendTopic:
    """Represents a trending topic from social media."""
    name: str
    volume: Optional[int] = None
    platform: str = "unknown"
    timestamp: datetime = datetime.now()
    metadata: Dict = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}
    
    @classmethod
    def from_x_data(cls, data: Dict) -> "TrendTopic":
        """Create a TrendTopic from X (Twitter) data."""
        return cls(
            name=data["name"],
            volume=data.get("tweet_volume"),
            platform="x",
            metadata=data
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "volume": self.volume,
            "platform": self.platform,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
