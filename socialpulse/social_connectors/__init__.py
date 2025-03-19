"""Social connectors for the SocialPulse module."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseSocialConnector(ABC):
    """Base class for social media platform connectors."""
    
    @abstractmethod
    def get_trending_topics(self, keywords: Optional[List[str]] = None, **kwargs) -> List[Dict]:
        """Get trending topics, optionally filtered by keywords."""
        pass
    
    @abstractmethod
    def search_posts(self, query: str, **kwargs) -> List[Dict]:
        """Search for posts/tweets matching a query."""
        pass
    
    def get_sentiment_for_topic(self, topic: str) -> Dict:
        """Get sentiment analysis for a specific topic."""
        raise NotImplementedError("Sentiment analysis not implemented for this connector")
