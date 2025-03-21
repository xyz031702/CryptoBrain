"""Base social connector class for SocialPulse module."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class BaseSocialConnector(ABC):
    """Base class for all social media connectors.
    
    All platform-specific connectors should inherit from this class
    and implement the required methods.
    """
    
    def __init__(self):
        """Initialize the base connector."""
        pass
