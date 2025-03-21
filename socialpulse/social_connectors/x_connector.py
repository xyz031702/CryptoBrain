"""X (formerly Twitter) connector for SocialPulse module.

cd to CryptoBrain directory
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
touch .env   # put into the X_API_KEY=sk-...
python -m socialpulse.social_connectors.x_connector

"""
import os
import sys
import json
import logging
import requests
from typing import List, Dict, Optional, Set, Tuple, Union, Any
from pathlib import Path
from datetime import datetime, timedelta

# Import base connector from local package
from socialpulse.social_connectors.base_connector import BaseSocialConnector

# Import exceptions
try:
    from socialpulse.exceptions import RateLimitException, AuthenticationException
except ImportError:
    # If running directly from socialpulse directory
    module_path = Path(__file__).resolve()
    sys.path.insert(0, str(module_path.parent.parent))
    from exceptions import RateLimitException, AuthenticationException

logger = logging.getLogger(__name__)

def load_profile(profile_path: str = None) -> Dict:
    """Load project profile from JSON file."""
    # Get the path to the profile directory
    module_path = Path(__file__).resolve()
    socialpulse_dir = module_path.parent.parent
    default_path = socialpulse_dir / "profile" / "profile.json"
    profile_path = profile_path or str(default_path)
    
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
    # Get the path to the profile directory
    module_path = Path(__file__).resolve()
    socialpulse_dir = module_path.parent.parent
    default_path = socialpulse_dir / "profile" / "track_x.json"
    track_path = track_path or str(default_path)
    
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
    """Connector for X (formerly Twitter) platform.
    
    Features:
    - Real API integration with the X API v2
    - Automatic fallback to mock data when no token is provided
    - Configurable rate limiting and error handling
    """
    
    def __init__(self, api_key: str = None, profile_path: str = None, track_path: str = None):
        """
        Initialize X connector with API credentials and profile data.
        
        Args:
            api_key: X API key for authentication
            api_secret: X API secret for authentication
            profile_path: Path to profile.json file
            track_path: Path to track_x.json file with accounts to track
        """
        self.api_key = api_key
        self.base_url = "https://alpha.pumpagent.ai/api"
        
        if not self.api_key:
            raise AuthenticationException("X_API_KEY is required for XConnector. Please provide a valid API key.")
        
        self.profile = load_profile(profile_path)
        self.track_accounts = load_track_accounts(track_path)
    
    def check_rate_limit(self) -> Dict[str, Any]:
        """
        Makes a lightweight API call to check if rate limit has been exceeded.
        
        Returns:
            Dict with rate limit status, containing:
                'ok': True if rate limits are OK, False if exceeded
                'limit': Total request limit if available
                'remaining': Remaining requests if available
                'reset': Time when limit resets (seconds since epoch) if available
                'message': Error message if any
                
        Raises:
            AuthenticationException: If no API key or secret is available
        """
        if not self.api_key:
            raise AuthenticationException("API key is required for X API calls")
            
        result = {
            'ok': False,
            'limit': None,
            'remaining': None,
            'reset': None,
            'message': None
        }
        
        try:
            # Use a lightweight API endpoint that doesn't consume many resources
            session = requests.Session()
            endpoint = "tool/twitter/user-info"
            url = f"{self.base_url}/{endpoint}/?username=web3hobby39067"
            
            # Set the API key in the header
            headers = {
                'Accept': 'application/json',
                'x-api-key': self.api_key
            }
            
            response = session.get(url, headers=headers)
            response.raise_for_status()
            print(response.text)
            # Extract response data
            result['ok'] = True
            
            # The alpha.pumpagent.ai API might have different rate limit headers
            # or include rate limit info in the response body
            # For now, we'll assume success if the request goes through
            result['limit'] = response.headers.get('x-ratelimit-limit', 'unknown')
            result['remaining'] = response.headers.get('x-ratelimit-remaining', 'unknown')
            result['reset'] = response.headers.get('x-ratelimit-reset', 'unknown')
            
            # Log the response for debugging
            logger.debug(f"Rate limit response: {response.text[:200]}...")
            logger.debug(f"Rate limit headers: {dict(response.headers)}")
            
            return result
            
        except requests.RequestException as e:
            result['ok'] = False
            
            if hasattr(e, 'response') and e.response:
                if e.response.status_code == 429:
                    result['message'] = "Rate limit exceeded"
                    # Extract rate limit headers if available
                    headers = e.response.headers
                    result['limit'] = headers.get('x-rate-limit-limit')
                    result['remaining'] = headers.get('x-rate-limit-remaining')
                    result['reset'] = headers.get('x-rate-limit-reset')
                else:
                    result['message'] = f"API error: {e}"
            else:
                result['message'] = f"Connection error: {e}"
                
            return result

    def get_account_tweets(self, account_handle: str, date_str: str = None) -> List[Dict]:
        """
        Get recent tweets from a specific X account using the X API v2.
        
        Args:
            account_handle: X account handle (with or without @)
            date_str: Date string in format 'yyyy-mm-dd' to filter tweets from
            count: Maximum number of tweets to return
            
        Returns:
            List of tweet dictionaries with content and metadata
        """
        # Remove @ if present in the handle
        handle = account_handle.lstrip('@')
        
        if not self.api_key:
            raise AuthenticationException("API key is required for X API calls")
            
        
        try:
            # Use a lightweight API endpoint that doesn't consume many resources
            session = requests.Session()
            endpoint = "tool/twitter/user-tweets"
            url = f"{self.base_url}/{endpoint}/?username={handle}"
            
            # Set the API key in the header
            headers = {
                'Accept': 'application/json',
                'x-api-key': self.api_key
            }
            
            response = session.get(url, headers=headers)
            result = response.json()
            
            # Process the response
            if not result or not isinstance(result, list):
                logger.warning(f"Invalid response format for user tweets: {result}")
                return []
                
            # Filter tweets by timestamp based on the given date or today
            if date_str:
                # Parse the date string in yyyy-mm-dd format
                try:
                    filter_date = datetime.strptime(date_str, '%Y-%m-%d')
                    filter_timestamp = int(filter_date.timestamp())
                except ValueError:
                    logger.warning(f"Invalid date format: {date_str}, using current date instead")
                    filter_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    filter_timestamp = int(filter_date.timestamp())
            else:
                filter_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                filter_timestamp = int(filter_date.timestamp())
            
            # Debug output
            print(f"Filter date: {filter_date.isoformat()}, Timestamp: {filter_timestamp}")
            print(f"Received {len(result)} tweets before filtering")
            if result and len(result) > 0:
                print(f"First tweet timestamp: {result[0].get('timestamp')}")
                print(f"First tweet date: {datetime.fromtimestamp(int(result[0].get('timestamp', 0))).isoformat()}")
            
            filtered_tweets = [tweet for tweet in result if int(tweet.get('timestamp', 0)) >= filter_timestamp]
            
            # Format the tweets to match our internal structure
            formatted_tweets = []
            for tweet in filtered_tweets:
                # Extract hashtags from text if not provided in API response
                hashtags = tweet.get("hashtags", [])
                if not hashtags and "text" in tweet:
                    # Extract hashtags from tweet text
                    words = tweet["text"].split()
                    hashtags = [word[1:] for word in words if word.startswith('#')]
                
                formatted_tweet = {
                    "id": tweet.get("id"),
                    "text": tweet.get("text"),
                    "created_at": datetime.fromtimestamp(int(tweet.get("timestamp", 0))).isoformat(),
                    "author": tweet.get("username"),
                    "metrics": {
                        "likes": tweet.get("likes", 0),
                        "retweets": tweet.get("retweets", 0),
                        "replies": tweet.get("replies", 0),
                        "views": tweet.get("views", 0)
                    },
                    "hashtags": hashtags,
                    "url": tweet.get("permanentUrl")
                }
                formatted_tweets.append(formatted_tweet)
            
            logger.info(f"Retrieved {len(formatted_tweets)} tweets from {handle}")
            print(formatted_tweets)
            return formatted_tweets
        except requests.RequestException as e:
            logger.error(f"Failed to fetch tweets: {e}")
            return {"error":"failed to get tweets"}
    
    def search_trendy_tweets(self, query: str, count: int = 10, date_str: str = None, min_likes: int = 10, min_retweets: int = 10) -> List[Dict]:
        """
        Search for trending tweets matching the query with additional filters.
        
        Args:
            query: Search query string
            count: Maximum number of tweets to return
            date_str: Optional date string in format 'yyyy-mm-dd' to filter tweets from
            min_likes: Minimum number of likes for tweets to include
            min_retweets: Minimum number of retweets for tweets to include
            sort_by: Field to sort by ('popular', 'recent', 'relevant')
            
        Returns:
            List of tweet dictionaries matching the search criteria ordered by popularity
        """
        if not self.api_key:
            raise AuthenticationException("API key is required for X API calls")
            
        try:
            # Prepare the request
            session = requests.Session()
            endpoint = "tool/twitter/search"
            url = f"{self.base_url}/{endpoint}"
            
            # Build query string with date filter if provided
            query_params = {}
            
            # Build the enhanced query with filters
            enhanced_query = query
            
            # Add date filter if provided
            if date_str:
                try:
                    # Validate date format
                    filter_date = datetime.strptime(date_str, '%Y-%m-%d')
                    # Add date to query
                    enhanced_query = f"{enhanced_query} since:{date_str}"
                except ValueError:
                    logger.warning(f"Invalid date format: {date_str}, using query without date filter")
            
            # Add popularity filters
            if min_likes is not None and min_likes > 0:
                enhanced_query = f"{enhanced_query} min_faves:{min_likes}"
            
            if min_retweets is not None and min_retweets > 0:
                enhanced_query = f"{enhanced_query} min_retweets:{min_retweets}"
            
            # Set the query parameter
            query_params['query'] = enhanced_query
                
            # Set max results
            query_params['maxResults'] = count
            
            # Set headers
            headers = {
                'Accept': 'application/json',
                'x-api-key': self.api_key
            }
            
            # Make the request
            response = session.get(url, params=query_params, headers=headers)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, dict):
                # Response is a dictionary with a 'data' field
                result = data.get('data', [])
            elif isinstance(data, list):
                # Response is directly a list
                result = data
            else:
                result = []
                
            logger.info(f"Found {len(result)} tweets matching query: {query}")
            return result
        except requests.RequestException as e:
            logger.error(f"Failed to search tweets: {e}")
            return []

# Usage example
if __name__ == "__main__":
    from dotenv import load_dotenv
    
    # Load environment variables from .env file if present
    # Set X_API_KEY and X_API_SECRET environment variables or add to .env file
    load_dotenv()
    
    # Create connector with API credentials

    try:
        connector = XConnector(
                api_key=os.getenv("X_API_KEY"), 
                profile_path="socialpulse/profile.json", 
                track_path="socialpulse/track_x.json"
            )
    except AuthenticationException as e:
        print(f"Authentication error: {e}")
        print("Please set X_API_KEY and X_API_SECRET environment variables with valid credentials")
        sys.exit(1)
    
    # Check rate limits before making any API calls
    print("\n--- Checking X API Rate Limits ---")
    rate_limit_status = connector.check_rate_limit()
    
    # Display rate limit information and exit if limits reached
    if rate_limit_status['ok']:
        print(f"Rate limits OK. Remaining requests: {rate_limit_status['remaining']}")
    else:
        print(f"Rate limit issue: {rate_limit_status['message']}, remaining: {rate_limit_status['remaining']}")
        print("Exiting due to rate limit restrictions.")
        sys.exit(1)
    # Example 1: Get tweets from a specific account with date filtering
    print("\n--- Example 1: Account Tweets with Date Filter ---")
    account_tweets = connector.get_account_tweets('@OpenSourceOrg', date_str='2025-03-19')
    print(f"Fetched {len(account_tweets)} tweets from OpenSourceOrg for 2025-03-19")
    
    # Example 2: Search for trending tweets ranked by popularity
    print("\n--- Example 2: Search for Trending Tweets (Popularity Ranked) ---")
    search_query = "crypto"  # Simple query term that should have many results
    search_date = "2025-03-19"  # Yesterday's date
    search_results = connector.search_trendy_tweets(
        query=search_query, 
        count=10,
        date_str=search_date,
        min_likes=5,           # Only tweets with at least 5 likes
        min_retweets=2,        # Only tweets with at least 2 retweets
    )
    print(f"Found {len(search_results)} popular tweets matching query: '{search_query}' since {search_date}")
    
    # Display first 3 search results, if any
    for i, tweet in enumerate(search_results[:3]):
        print(f"\nTweet {i+1}:")
        print(f"Text: {tweet.get('text', 'No text')[:100]}...")
        
        # Get username based on the fields available in the actual API response
        username = tweet.get('username', 'Unknown')
        print(f"Author: @{username}")
        
        # Handle timestamp (convert from Unix epoch if present)
        if 'timestamp' in tweet:
            # Convert timestamp to human-readable format
            tweet_time = datetime.fromtimestamp(tweet['timestamp'])
            formatted_time = tweet_time.strftime("%Y-%m-%d %H:%M")
            print(f"Created at: {formatted_time}")
        else:
            print(f"Created at: {tweet.get('created_at', 'Unknown')}")
            
        # Show engagement metrics
        likes = tweet.get('likes', 0)
        retweets = tweet.get('retweets', 0)
        views = tweet.get('views', 0)
        replies = tweet.get('replies', 0)
        
        print(f"Likes: {likes}")
        print(f"Retweets: {retweets}")
        print(f"Views: {views}")
        print(f"Replies: {replies}")
        print(f"URL: {tweet.get('permanentUrl', '')}")



    print("\n--- Example 3: Get relevant content filtered by profile ---")


