"""X (formerly Twitter) connector for SocialPulse module."""

import os
import json
import logging
import requests
from typing import List, Dict, Optional, Set, Tuple, Union
from pathlib import Path

from social_connectors import BaseSocialConnector
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to sys.path to import exceptions
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from exceptions import RateLimitException, AuthenticationException

logger = logging.getLogger(__name__)

def load_profile(profile_path: str = None) -> Dict:
    """Load project profile from JSON file."""
    default_path = os.path.join(parent_dir, "profile", "profile.json")
    profile_path = profile_path or default_path
    
    try:
        with open(profile_path, 'r') as f:
            profile = json.load(f)
            logger.info(f"Loaded profile for {profile.get('name', 'unknown project')}")
            return profile
    except Exception as e:
        logger.error(f"Error loading profile from {profile_path}: {e}")
        return {}

def load_track_accounts(track_path: str = None) -> List[Dict]:
    """Load X accounts to track from JSON file."""
    default_path = os.path.join(parent_dir, "profile", "track_x.json")
    track_path = track_path or default_path
    
    try:
        with open(track_path, 'r') as f:
            data = json.load(f)
            accounts = data.get("accounts", [])
            logger.info(f"Loaded {len(accounts)} X accounts to track")
            return accounts
    except Exception as e:
        logger.error(f"Error loading track accounts from {track_path}: {e}")
        return []

class XConnector(BaseSocialConnector):
    """Connector for X (formerly Twitter) platform."""
    
    def __init__(self, bearer_token: str = None, profile_path: str = None, track_path: str = None):
        """
        Initialize X connector with API credentials and profile data.
        
        Args:
            bearer_token: X Bearer token for API authentication
            profile_path: Path to profile.json file
            track_path: Path to track_x.json file with accounts to track
        """
        self.bearer_token = bearer_token or os.environ.get("X_BEARER_TOKEN")
        self.base_url = "https://api.twitter.com/2"
        self.session = self._create_session()
        self.profile = load_profile(profile_path)
        self.track_accounts = load_track_accounts(track_path)
        self.last_trends_check = None
        self.trend_check_interval = timedelta(minutes=30)  # Check trends every 30 minutes
        self.last_accounts_check = None
        self.accounts_check_interval = timedelta(hours=6)  # Check account tweets every 6 hours
        
    # Token acquisition is handled externally
            
    def _create_session(self) -> requests.Session:
        """Create authenticated session for X API."""
        session = requests.Session()
        if self.bearer_token:
            session.headers.update({"Authorization": f"Bearer {self.bearer_token}"})
        return session
        
    def update_profile(self, profile_path: str = None):
        """Update the profile data."""
        self.profile = load_profile(profile_path)
    
    def update_track_accounts(self, track_path: str = None):
        """Update the track accounts data."""
        self.track_accounts = load_track_accounts(track_path)
        
    # Token lifecycle is handled externally
    
    def get_account_tweets(self, account_handle: str, count: int = 10) -> List[Dict]:
        """
        Get recent tweets from a specific X account.
        
        Args:
            account_handle: X account handle (with or without @)
            count: Maximum number of tweets to return
            
        Returns:
            List of tweet dictionaries with content and metadata
        """
        # Remove @ if present in the handle
        handle = account_handle.lstrip('@')
        
        # In a real implementation, this would use the X API to get tweets
        # For now, create mock data based on the account handle
        logger.info(f"Fetching {count} tweets from {handle}")
        
        # Get account info for more realistic mock data
        account_info = next((acc for acc in self.track_accounts if acc["handle"].lstrip('@') == handle), None)
        
        tweets = []
        current_time = datetime.now()
        
        # Generate mock tweets
        for i in range(count):
            # Create time with decreasing recency
            tweet_time = current_time - timedelta(hours=i*3)
            
            # Create tweet with content that matches account focus
            description = account_info["description"] if account_info else f"Content from {handle}"
            topic_words = description.split()[:3]  # Take first few words for topic simulation
            
            tweet = {
                "id": f"{handle}-{i}",
                "text": self._generate_mock_tweet(handle, topic_words),
                "created_at": tweet_time.isoformat(),
                "author": handle,
                "metrics": {
                    "likes": random.randint(5, 1000),
                    "retweets": random.randint(0, 200),
                    "replies": random.randint(0, 50)
                }
            }
            tweets.append(tweet)
            
        return tweets
    
    def _generate_mock_tweet(self, handle: str, topic_words: List[str]) -> str:
        """
        Generate a realistic mock tweet based on account and topics.
        
        Args:
            handle: Account handle
            topic_words: List of topic-related words
            
        Returns:
            Generated tweet text
        """
        # Templates for realistic tweets
        templates = [
            "Just published our latest {topic} update. Check it out! #{topic2} #{topic3}",
            "Excited to announce a new {topic} integration with {topic2}. More details coming soon!",
            "Our team is working on improving {topic} functionality. Any feature requests? #{topic3}",
            "Today's {topic} market is showing interesting trends in {topic2}. Thoughts? #{topic3}",
            "New research suggests {topic} will play a key role in future {topic2} development. #{topic3}",
            "Looking for feedback on our recent {topic} release. What do you think about the {topic2} features?",
            "Join us for a live discussion on {topic} and {topic2} next week! Register now. #{topic3}",
        ]
        
        # Ensure we have enough topic words
        while len(topic_words) < 3:
            topic_words.append(random.choice(["technology", "innovation", "development", "update"]))
        
        # Select a template and fill it
        template = random.choice(templates)
        return template.format(
            topic=topic_words[0],
            topic2=topic_words[1],
            topic3=topic_words[2].replace(' ', '')
        )
    
    def get_all_track_account_tweets(self, tweets_per_account: int = 5) -> Dict[str, List[Dict]]:
        """
        Get recent tweets from all tracked accounts.
        
        Args:
            tweets_per_account: Number of tweets to fetch per account
            
        Returns:
            Dictionary mapping account handles to lists of tweets
        """
        # Check if we need fresh data based on time interval
        current_time = datetime.now()
        if (self.last_accounts_check and 
            current_time - self.last_accounts_check < self.accounts_check_interval):
            logger.info("Using cached track account tweets")
            # In a real implementation, return cached tweets here
            # For now, we'll always generate fresh mock data
        
        self.last_accounts_check = current_time
        
        # If no track accounts, return empty dict
        if not self.track_accounts:
            logger.warning("No track accounts configured, use update_track_accounts() method")
            return {}
            
        logger.info(f"Fetching tweets from {len(self.track_accounts)} tracked accounts")
        
        # Fetch tweets for each account
        all_tweets = {}
        for account in self.track_accounts:
            handle = account["handle"]
            all_tweets[handle] = self.get_account_tweets(handle, tweets_per_account)
            
        return all_tweets
    
    def _extract_profile_filters(self) -> Tuple[List[str], List[str]]:
        """
        Extract keywords and hashtags from profile for filtering.
        
        Returns:
            Tuple containing (keywords, hashtags) lists
        """
        keywords = self.profile.get('keywords', [])
        # Strip hashtag symbol from profile hashtags for easier comparison
        hashtags = [tag.lstrip('#').lower() for tag in self.profile.get('hashtags', [])]
        return keywords, hashtags

    def get_trending_topics(self, location_id: str = "1", use_profile: bool = True) -> List[Dict]:
        """
        Get trending topics from X, optionally filtered by profile data.
        
        Args:
            location_id: WOEID (Where On Earth ID) for location-specific trends
            use_profile: Whether to filter trends by profile keywords and hashtags
            
        Returns:
            List of trending topics with relevance scores if filtered by profile
        """
        try:
            # Check if we need to refresh trends based on time interval
            current_time = datetime.now()
            if (self.last_trends_check is None or 
                (current_time - self.last_trends_check) > self.trend_check_interval):
                # In a real implementation, this would make an API call to fetch fresh trends
                # For simplicity, we're using mock data
                self.last_trends_check = current_time
                
            # Get mock trends dynamically based on profile data if available
            if self.profile:
                # Extract terms from profile to create more relevant mock trends
                profile_terms = []
                # Add hashtags without the # symbol
                profile_terms.extend([tag.strip('#') for tag in self.profile.get('hashtags', [])])
                # Add selected keywords
                profile_terms.extend(self.profile.get('keywords', []))
                # Add unique components (shortened)
                for component in self.profile.get('unique_components', []):
                    term = component.split(':', 1)[0].strip() if ':' in component else component.strip()
                    profile_terms.append(term)
                
                # Create mock trends using profile data
                trends = [
                    {"name": f"#{term.replace(' ', '')}", "tweet_volume": 50000 - (i * 3000)} 
                    for i, term in enumerate(profile_terms[:12])
                ]
            else:
                logger.warning("No profile data available for trend filtering")
                trends = []
            
            # If not using profile for filtering, return all trends
            if not use_profile or not self.profile:
                return trends
                
            # Filter and score trends based on profile data
            keywords, hashtags = self._extract_profile_filters()
            
            if not keywords and not hashtags:
                logger.warning("No keywords or hashtags found in profile for filtering")
                return trends
                
            scored_trends = []
            for trend in trends:
                trend_text = trend["name"].lstrip('#').lower()
                relevance_score = 0
                matches = []
                
                # Check for hashtag matches (higher weight)
                for tag in hashtags:
                    if tag == trend_text or tag in trend_text:
                        relevance_score += 2
                        matches.append(f"hashtag:{tag}")
                
                # Check for keyword matches
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    if keyword_lower == trend_text or keyword_lower in trend_text:
                        relevance_score += 1
                        matches.append(f"keyword:{keyword}")
                
                # Add trend with relevance info if it matches
                if relevance_score > 0:
                    trend_copy = trend.copy()
                    trend_copy["relevance_score"] = relevance_score
                    trend_copy["matches"] = matches
                    scored_trends.append(trend_copy)
            
            # Sort by relevance score (descending)
            return sorted(scored_trends, key=lambda x: x["relevance_score"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error fetching trending topics from X: {str(e)}")
            return []
    
    def search_posts(self, query: str = None, count: int = 10, use_profile: bool = False) -> List[Dict]:
        """
        Search for tweets matching a query or using profile data.
        
        Args:
            query: Search query (optional if use_profile is True)
            count: Number of posts to return
            use_profile: Whether to use profile data for search
            
        Returns:
            List of posts matching the criteria
        """
        try:
            search_terms = []
            
            # Use explicit query if provided
            if query:
                search_terms.append(query)
                
            # Add profile-based search terms if requested
            if use_profile and self.profile:
                keywords, hashtags = self._extract_profile_filters()
                
                # Add keywords from profile
                search_terms.extend(keywords)
                
                # Add hashtags from profile (with # prefix)
                search_terms.extend([f"#{tag}" for tag in hashtags])
            
            # If no search terms available, return empty list
            if not search_terms:
                logger.warning("No search terms provided or found in profile")
                return []
                
            # Log what we're searching for
            logger.info(f"Searching X for posts with terms: {search_terms}")
            
            # Mock response for demonstration
            # In a real implementation, we would send queries to the X API with the search terms
            mock_results = []
            for i in range(count):
                # Generate a different text for each search term to simulate varied results
                term_index = i % len(search_terms)
                search_term = search_terms[term_index]
                
                mock_results.append({
                    "id": f"tweet_{i}",
                    "text": f"This is a mock tweet about {search_term} with some additional content for demonstration",
                    "user": {"username": f"user_{i}", "followers": 5000 - i*100},
                    "engagement": {"retweets": 45 - i, "likes": 130 - i*10},
                    "created_at": "2025-03-19T12:00:00Z",
                    "search_term_matched": search_term
                })
                
            return mock_results
            
        except Exception as e:
            logger.error(f"Error searching tweets on X: {str(e)}")
            return []

    def get_relevant_content(self, max_trends: int = 5, max_posts_per_trend: int = 3, 
                             track_tweets_per_account: int = 2) -> Dict[str, Any]:
        """
        Integrated approach that combines passive trend monitoring with active searching and account tracking.
        This method uses the profile data to:
        1. Get trending topics filtered by profile relevance
        2. For each relevant trend, search for posts about that trend
        3. Get tweets from tracked accounts defined in track_x.json
        
        Args:
            max_trends: Maximum number of trends to process
            max_posts_per_trend: Maximum number of posts to fetch per trend
            track_tweets_per_account: Number of tweets to fetch per tracked account
            
        Returns:
            Dictionary with relevant trends, associated posts, and tracked account tweets
        """
        if not self.profile:
            logger.warning("No profile data available for content filtering")
            return {"trends": [], "posts": [], "track_tweets": {}}
        
        # Get trends filtered by profile
        trends = self.get_trending_topics(use_profile=True)
        relevant_trends = trends[:max_trends] if len(trends) > max_trends else trends
        
        # For each relevant trend, fetch related posts
        trend_posts = {}
        for trend in relevant_trends:
            trend_name = trend["name"]
            # Search for posts related to this trend
            posts = self.search_posts(query=trend_name, count=max_posts_per_trend)
            trend_posts[trend_name] = posts
        
        # Also get posts based on profile keywords
        keyword_posts = self.search_posts(use_profile=True, count=max_posts_per_trend * 2)
        
        # Get tweets from tracked accounts
        track_tweets = self.get_all_track_account_tweets(tweets_per_account=track_tweets_per_account)
        
        return {
            "trends": relevant_trends,
            "trend_posts": trend_posts,
            "keyword_posts": keyword_posts,
            "track_tweets": track_tweets
        }

# Usage example
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    # Load environment variables from .env file if present
    load_dotenv()
    
    # Create connector with bearer token
    # Option 1: Pass token directly
    # connector = XConnector(bearer_token="YOUR_BEARER_TOKEN")
    
    # Option 2: Use environment variable
    # Set X_BEARER_TOKEN environment variable or add to .env file
    connector = XConnector()
    
    # Example 1: Get all tweets from tracked accounts with their hashtags and keywords
    print("\n--- Example 1: Account Tracking ---")
    track_tweets = connector.get_all_track_account_tweets(tweets_per_account=3)
    track_handles = list(track_tweets.keys())
    print(f"Tracking {len(track_handles)} accounts")
    for handle in track_handles[:3]:  # Show first 3 accounts
        print(f"\nTweets from {handle}:")
        for tweet in track_tweets[handle]:
            # Extract hashtags from tweet text
            words = tweet['text'].split()
            hashtags = [word for word in words if word.startswith('#')]
            print(f"- {tweet['text'][:80]}...")
            print(f"  Hashtags: {', '.join(hashtags) if hashtags else 'None'}")
    
    # Example 2: Find trending topics related to our tracked accounts
    print("\n--- Example 2: Related Trending Topics ---")
    # In a real implementation, this would find trends related to our tracked accounts
    # For now, we use the profile-filtered trends as a proxy
    profile_trends = connector.get_trending_topics(use_profile=True)
    print(f"Found {len(profile_trends)} trending topics related to tracked accounts:")
    for trend in profile_trends[:5]:  # Show top 5
        print(f"- {trend['name']} (Relevance: {trend.get('relevance_score', 'N/A')})")
    
    # Example 3: Get relevant content filtered by profile
    print("\n--- Example 3: Complete Content Pipeline ---")
    relevant_content = connector.get_relevant_content(max_trends=3, max_posts_per_trend=2, track_tweets_per_account=2)
    
    # Show stats
    print(f"Pipeline results:")
    print(f"- {len(relevant_content['track_tweets'])} accounts tracked")
    print(f"- {len(relevant_content['trends'])} relevant trending topics")
    print(f"- {sum(len(posts) for posts in relevant_content['trend_posts'].values())} posts from trends")
    print(f"- {len(relevant_content['keyword_posts'])} posts from profile keywords")
    
    # Show sample of content
    if relevant_content['trends']:
        trend = relevant_content['trends'][0]['name']
        posts = relevant_content['trend_posts'].get(trend, [])
        if posts:
            print(f"\nSample posts for trend '{trend}':")
            for post in posts[:2]:
                print(f"- {post['text'][:80]}...")

