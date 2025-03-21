# Social Connectors

This module provides connectors to various social media platforms for the SocialPulse system.

## Connector Workflow

The connector module follows a simple workflow focused on data retrieval and processing:

1. **Authentication** - Connect to API using bearer token from environment variable
2. **Data Retrieval** - Fetch content from accounts you're tracking 
3. **Processing** - Extract hashtags, keywords, and sentiment
4. **Rate Limit Management** - Exit gracefully when limits are reached

## Operating Modes

The connector supports two primary operating modes:

### 1. Account Tracking Mode

Track specific accounts defined in your configuration:

```python
# Get content from tracked accounts
tracked_content = connector.get_all_track_account_tweets()
```

### 2. Topic Discovery Mode

Discover trending topics and relevant content based on your profile:

```python
# Get trending topics related to your interests
trends = connector.get_trending_topics(use_profile=True)

# Get relevant content based on profile
relevant_content = connector.get_relevant_content()
```

## Error Handling

The connector implements simple error handling for authentication and rate limits:

```python
try:
    connector = XConnector()
    content = connector.get_account_tweets("example")
except AuthenticationException as e:
    print(f"Authentication error: {e}")
    sys.exit(1)
```

When rate limits are exceeded, the connector will exit with an appropriate message.

