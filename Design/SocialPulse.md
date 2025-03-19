# SocialPulse: Technical Design Document

This document provides a high-level, maintainable overview of the SocialPulse system without diagrams or detailed code. The design leverages connectors for external data, a lean local analyzer for processing, and implements a specific dataflow from platform monitoring to human-approved posting.

---

## 1. Overview

SocialPulse monitors social media platforms to identify trending topics and key accounts, matches them against our profile for relevance, and generates content suggestions that undergo a refinement period before being submitted for human approval via GitLab issues. This approach ensures high-quality, relevant content while maintaining human oversight before publication.

---

## 2. System Components

### 2.1 Social Media Connector
- **Purpose:**  
  Collects data from various social platforms (e.g., Twitter/X, Reddit, Telegram, Discord) using native APIs.
- **Key Points:**  
  - Implements an adapter pattern with provider-specific modules.
  - Normalizes data into a consistent JSON format for further processing.
  - Manages API rate limits and authentication transparently.

### 2.2 Trend Analysis Engine
- **Purpose:**  
  Identifies trending topics (hashtags, keywords) and key accounts across platforms.
- **Key Points:**  
  - Uses a service gateway pattern for asynchronous data fetching.
  - Applies caching strategies with configurable time-to-live (TTL) values.
  - Maintains separate tracking for topics and influential accounts.

### 2.3 Profile Matching System
- **Purpose:**  
  Evaluates relevance of trending topics and accounts against our profile.
- **Key Points:**  
  - Maintains a profile database with our descriptions and main social accounts.
  - Uses semantic matching algorithms to determine relevance scores.
  - Integrates with predefined topics and key accounts (offline preprocessed).

### 2.4 Data Feed Listener
- **Purpose:**  
  Continuously monitors relevant data sources based on matched topics.
- **Key Points:**  
  - Implements efficient streaming connections where available.
  - Uses polling with optimized intervals for other platforms.
  - Filters incoming data based on relevance to our profile.

### 2.5 Content Generation Engine
- **Purpose:**  
  Brainstorms and refines potential posts based on relevant feeds.
- **Key Points:**  
  - Implements a "think window" (2-hour period) for content refinement.
  - Uses template-based generation with LLM enhancement.
  - Produces multiple content variations for human selection.

### 2.6 GitLab Integration
- **Purpose:**  
  Creates issues for human approval of generated content.
- **Key Points:**  
  - Automatically generates structured GitLab issues with content previews.
  - Includes metadata about source trends and relevance scores.
  - Provides one-click approval mechanism for streamlined workflow.

### 2.7 Publishing System
- **Purpose:**  
  Posts approved content to appropriate social platforms.
- **Key Points:**  
  - Manages scheduling and cross-platform formatting.
  - Handles authentication and API interactions.
  - Tracks performance metrics for feedback into the system.

---

## 3. Detailed Dataflow

### 3.1 Platform Monitoring → Trend Identification
- Social Media Connector continuously monitors platforms (X, Reddit, etc.)
- Trend Analysis Engine identifies:
  - Trending hashtags and search keywords
  - Key accounts with high engagement or influence
- System maintains separate databases for topics and accounts

### 3.2 Relevance Matching
- Profile Matching System evaluates trends and accounts against our profile:
  - Compares with our account descriptions and social media presence
  - Scores relevance based on semantic similarity and historical engagement
- System incorporates predefined topics and key accounts (offline preprocessed)
  - These serve as a baseline for relevance matching
  - Regularly updated through manual curation

### 3.3 Data Feed Processing
- Data Feed Listener activates based on matched topics and accounts
- Continuously monitors relevant sources with optimized polling
- Performs real-time relevance matching on incoming content
  - Filters out low-relevance items
  - Prioritizes high-relevance content for analysis

### 3.4 Content Generation
- Content Generation Engine processes relevant feeds:
  - Brainstorms potential post ideas based on trending topics
  - Considers our historical content style and engagement patterns
- Implements a 2-hour "think window" for content refinement:
  - Initial draft generation
  - Periodic refinement as new data arrives
  - Final polishing before submission

### 3.5 Human Approval Workflow
- System generates GitLab issues for human approval:
  - Structured format with content preview
  - Source attribution and relevance metrics
  - Multiple content variations when appropriate
- Human reviewers approve, reject, or modify content
- Approval triggers the publishing process

### 3.6 Publishing
- Publishing System handles approved content:
  - Formats appropriately for target platforms
  - Schedules posting at optimal times
  - Manages API interactions and authentication
- Performance metrics are collected and fed back into the system

---

## 4. API Endpoints and Configuration

### 4.1 Internal API Endpoints
SocialPulse exposes a set of internal RESTful APIs for integration and management:

- **Platform Monitoring API:**
  - Configure platforms and authentication
  - Adjust monitoring parameters

- **Trend Analysis API:**
  - Retrieve current trending topics and accounts
  - Configure trend detection parameters

- **Profile Management API:**
  - Update our profile descriptions
  - Manage predefined topics and accounts

- **Content Generation API:**
  - Trigger manual content generation
  - Adjust think window parameters

- **GitLab Integration API:**
  - Configure issue templates
  - Manage approval workflows

- **Publishing API:**
  - Schedule and manage posts
  - Retrieve performance metrics

### 4.2 Configuration

- **Platforms:**
  - API keys and authentication details
  - Rate limits and polling intervals
  - Platform-specific formatting templates

- **Profile:**
  - Our account descriptions and keywords
  - Historical content analysis
  - Relevance scoring parameters

- **Content Generation:**
  - Think window duration (default: 2 hours)
  - Template configurations
  - LLM integration parameters

- **GitLab:**
  - Project ID and authentication
  - Issue templates and labels
  - Webhook configurations

- **Publishing:**
  - Platform-specific posting parameters
  - Scheduling preferences
  - Performance tracking configuration

---

## 5. Deployment and Maintenance

- **Local Development:**  
  Leverages Python, Docker, and a persistent database for rapid development and testing.

- **Scalability:**  
  Modular architecture with separate services for each major component:
  - Platform monitoring services can scale independently
  - Content generation can be distributed across multiple nodes
  - GitLab integration and publishing run as separate services

- **Monitoring:**  
  Comprehensive logging and metrics tracking:
  - Platform connectivity status
  - Trend detection performance
  - Content generation metrics
  - Approval rates and turnaround times
  - Publishing success rates

- **Maintainability:**  
  - Configuration-driven approach for easy updates
  - Clear separation of concerns between components
  - Extensive documentation of APIs and dataflows
  - Regular performance reviews and optimization

---

## 6. System Technical Requirements

### 6.1 Core Technologies

- **Programming Language:** Python 3.9+
  - Asyncio for asynchronous operations
  - FastAPI for internal API endpoints
  - Pydantic for data validation and settings management

- **Containerization:** Docker
  - Individual containers for each major component
  - Docker Compose for local development
  - Kubernetes for production deployment (optional)

- **Message Broker:** Redis
  - Required for inter-component communication
  - Used for task queuing and pub/sub messaging
  - Enables real-time updates across components

- **Caching Layer:** Redis
  - Required for high-performance caching
  - Stores frequently accessed data (trends, profile matches)
  - Reduces load on primary databases and external APIs

- **Task Processing:** Celery
  - Handles background tasks and scheduled operations
  - Manages the content refinement during the "think window"
  - Coordinates with Redis for task distribution

- **GitLab Integration:** GitLab API
  - Python-GitLab library for issue management
  - Webhook handlers for approval notifications

### 6.2 Database Architecture

#### Primary Databases

- **MongoDB (Document Store)**
  - **Collections:**
    - `social_posts`: Stores raw and processed social media posts
    - `trending_topics`: Tracks trending hashtags and keywords
    - `key_accounts`: Maintains information about influential accounts
    - `content_drafts`: Stores content during the refinement process
    - `published_content`: Archives all published posts with performance data
  - **Advantages:**
    - Flexible schema for varied social media data formats
    - Good performance for read-heavy operations
    - Native support for JSON data structures

- **PostgreSQL (Relational)**
  - **Tables:**
    - `profiles`: Our profile definitions and configurations
    - `predefined_topics`: Manually curated topics of interest
    - `relevance_scores`: Historical relevance matching data
    - `platform_credentials`: API keys and authentication details
    - `system_configuration`: Global system settings
  - **Advantages:**
    - Strong data integrity for configuration data
    - Complex query capabilities for analytics
    - Transaction support for critical operations

#### Redis Usage (Required)

Redis is essential for SocialPulse for several reasons:

1. **Real-time Data Processing**
   - **Pub/Sub Channels:**
     - `trending:updates`: Broadcasts newly detected trends
     - `content:drafts`: Notifies about content updates during refinement
     - `approval:notifications`: Alerts about human approval actions
   - **Sorted Sets:**
     - Ranks trending topics by relevance and recency
     - Prioritizes content drafts during the think window

2. **Caching Layer**
   - **Key-Value Store:**
     - Caches API responses to reduce external calls
     - Stores computed relevance scores
     - Maintains session data for admin interfaces
   - **TTL-based Expiration:**
     - Automatically expires cached data based on freshness requirements
     - Different TTLs for different data types (e.g., trends vs. account info)

3. **Task Queuing**
   - **Lists:**
     - Queues for content generation tasks
     - Scheduled posting operations
     - Data collection jobs
   - **Integration with Celery:**
     - Serves as the broker for Celery tasks
     - Enables distributed task processing

4. **Rate Limiting**
   - **Counters:**
     - Tracks API usage for external services
     - Implements sliding window rate limiting
     - Prevents exceeding platform-specific API quotas

### 6.3 Storage Requirements

- **MongoDB:** 50-100GB (depends on retention policy)
  - Primarily for social media data and content archives
  - Consider time-based partitioning for historical data

- **PostgreSQL:** 5-10GB
  - Configuration and relationship data
  - Analytics and reporting tables

- **Redis:** 2-5GB RAM
  - In-memory data for active operations
  - Consider Redis persistence for recovery

- **File Storage:** 10-20GB
  - Logs and system backups
  - Media attachments (if stored locally)

### 6.4 Network Requirements

- **External APIs:**
  - Reliable internet connection with low latency
  - Bandwidth for continuous data streaming (minimum 10Mbps)
  - Support for persistent connections where available

- **Internal Communication:**
  - Fast local network for inter-service communication
  - Service discovery mechanism for containerized deployment

---

## 7. Summary

SocialPulse implements a comprehensive dataflow from platform monitoring to human-approved posting. The system identifies trending topics and key accounts across social platforms, matches them against our profile for relevance, continuously monitors relevant feeds, generates and refines content over a 2-hour think window, submits content for human approval via GitLab issues, and finally publishes approved content to appropriate platforms.

The system requires Python 3.9+, Docker for containerization, and a multi-database approach with MongoDB for flexible document storage, PostgreSQL for relational data, and Redis for caching, messaging, and task queuing. Redis is essential for enabling real-time operations, efficient caching, and distributed task processing across the platform's components.

This approach ensures that our social media presence remains relevant, timely, and high-quality, while maintaining human oversight throughout the process. The modular architecture allows for easy scaling and maintenance, while the configuration-driven approach enables quick adjustments to changing requirements.

---

## 8. Folder Structure

Below is the recommended folder structure for the SocialPulse module implementation, with improvements to support domain-specific functionality, enhanced monitoring, and better component organization:

```
socialpulse/
├── README.md                       # Module documentation
├── pyproject.toml                  # Project dependencies and metadata
├── setup.py                        # Installation script
├── .env.example                    # Example environment variables
├── .gitignore                      # Git ignore file
├── docker/
│   ├── Dockerfile                  # Main service Dockerfile
│   ├── docker-compose.yml          # Local development setup
│   └── docker-compose.prod.yml     # Production deployment setup
│
├── socialpulse/                    # Main package
│   ├── __init__.py                 # Package initialization
│   ├── main.py                     # Application entry point
│   ├── config.py                   # Configuration management
│   ├── constants.py                # System constants
│   ├── exceptions.py               # Custom exceptions
│   │
│   ├── api/                        # API endpoints
│   │   ├── __init__.py
│   │   ├── router.py               # FastAPI router setup
│   │   ├── platform.py             # Platform monitoring endpoints
│   │   ├── trends.py               # Trend analysis endpoints
│   │   ├── profile.py              # Profile management endpoints
│   │   ├── content.py              # Content generation endpoints
│   │   ├── gitlab.py               # GitLab integration endpoints
│   │   └── publishing.py           # Publishing endpoints
│   │
│   ├── core/                       # Core functionality
│   │   ├── __init__.py
│   │   ├── db/                     # Database connections
│   │   │   ├── __init__.py
│   │   │   ├── mongo.py            # MongoDB client
│   │   │   ├── postgres.py         # PostgreSQL client
│   │   │   └── redis.py            # Redis client
│   │   │
│   │   ├── cache/                  # Caching utilities
│   │   │   ├── __init__.py
│   │   │   └── managers.py         # Cache management
│   │   │
│   │   └── tasks/                  # Background tasks
│   │       ├── __init__.py
│   │       ├── celery_app.py       # Celery configuration
│   │       ├── scheduler.py        # Task scheduling
│   │       └── workers.py          # Task workers
│   │
│   ├── connectors/                 # External connectors
│   │   ├── __init__.py
│   │   ├── base.py                 # Base connector class
│   │   ├── social/                 # Social media connectors
│   │   │   ├── __init__.py
│   │   │   ├── twitter.py          # Twitter/X connector
│   │   │   ├── reddit.py           # Reddit connector
│   │   │   ├── telegram.py         # Telegram connector
│   │   │   └── discord.py          # Discord connector
│   │   │
│   │   └── gitlab/                 # GitLab integration
│   │       ├── __init__.py
│   │       ├── client.py           # GitLab API client
│   │       ├── webhooks.py         # Webhook handlers
│   │       ├── templates/          # Issue templates
│   │       ├── workflows/          # Approval workflows
│   │       └── notifications.py    # Notification system
│   │
│   ├── domain/                     # Domain-specific functionality
│   │   ├── __init__.py
│   │   └── crypto/                 # Cryptocurrency domain
│   │       ├── __init__.py
│   │       ├── market_data.py      # Crypto market data processing
│   │       ├── terminology.py      # Crypto-specific terminology
│   │       └── indicators.py       # Crypto market indicators
│   │
│   ├── engines/                    # Core processing engines
│   │   ├── __init__.py
│   │   ├── trend_analysis.py       # Trend analysis engine
│   │   ├── profile_matching.py     # Profile matching system
│   │   ├── data_feed.py            # Data feed listener
│   │   ├── content_generation.py   # Content generation engine
│   │   ├── publishing.py           # Publishing system
│   │   └── think_window/           # 2-hour refinement window
│   │       ├── __init__.py
│   │       ├── scheduler.py        # Manages refinement scheduling
│   │       ├── stages.py           # Defines refinement stages
│   │       └── version_control.py  # Tracks content versions
│   │
│   ├── llm/                        # LLM integration
│   │   ├── __init__.py
│   │   ├── providers/              # Different LLM providers
│   │   │   ├── __init__.py
│   │   │   ├── openai.py           # OpenAI integration
│   │   │   └── anthropic.py        # Anthropic integration
│   │   ├── prompts/                # Prompt templates
│   │   │   ├── __init__.py
│   │   │   ├── trend_analysis.py   # Trend analysis prompts
│   │   │   └── content_gen.py      # Content generation prompts
│   │   ├── fine_tuning.py          # Fine-tuning utilities
│   │   └── tokenizer.py            # Token handling
│   │
│   ├── middlewares/                # Middleware components
│   │   ├── __init__.py
│   │   ├── authentication.py       # Authentication middleware
│   │   ├── rate_limiting.py        # Rate limiting middleware
│   │   └── logging.py              # Request logging middleware
│   │
│   ├── models/                     # Data models
│   │   ├── __init__.py
│   │   ├── social_post.py          # Social post model
│   │   ├── trend.py                # Trend model
│   │   ├── account.py              # Account model
│   │   ├── profile.py              # Profile model
│   │   ├── content.py              # Content model
│   │   └── issue.py                # GitLab issue model
│   │
│   ├── monitoring/                 # Monitoring and observability
│   │   ├── __init__.py
│   │   ├── prometheus.py           # Prometheus metrics
│   │   ├── logging.py              # Structured logging
│   │   ├── alerts.py               # Alert management
│   │   └── dashboards/             # Dashboard definitions
│   │       ├── __init__.py
│   │       ├── grafana.py          # Grafana dashboard configs
│   │       └── prometheus.py       # Prometheus dashboard configs
│   │
│   ├── schemas/                    # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── requests/               # Request schemas
│   │   │   ├── __init__.py
│   │   │   └── *.py                # Various request schemas
│   │   │
│   │   └── responses/              # Response schemas
│   │       ├── __init__.py
│   │       └── *.py                # Various response schemas
│   │
│   └── utils/                      # Utility functions
│       ├── __init__.py
│       ├── logging.py              # Logging configuration
│       ├── metrics.py              # Metrics collection
│       ├── rate_limiting.py        # Rate limiting utilities
│       └── text_processing.py      # Text processing utilities
│
├── alembic/                        # Database migrations
│   ├── versions/                   # Migration versions
│   └── env.py                      # Alembic environment
│
├── config/                         # Configuration files
│   ├── settings.yaml               # Default settings
│   ├── platforms.yaml              # Platform configurations
│   ├── profiles.yaml               # Profile definitions
│   ├── templates.yaml              # Content templates
│   ├── versions/                   # Versioned configurations
│   ├── migrations/                 # Configuration migrations
│   └── validators/                 # Configuration validators
│
├── docs/                           # Documentation
│   ├── api/                        # API documentation
│   ├── guides/                     # Developer guides
│   ├── architecture/               # Architecture diagrams
│   └── examples/                   # Usage examples
│
├── scripts/                        # Utility scripts
│   ├── setup_db.py                 # Database setup
│   ├── seed_data.py                # Seed initial data
│   └── backup.py                   # Backup utilities
│
└── tests/                          # Test suite
    ├── __init__.py
    ├── conftest.py                 # Test configuration
    ├── test_api/                   # API tests
    ├── test_connectors/            # Connector tests
    ├── test_engines/               # Engine tests
    ├── test_models/                # Model tests
    ├── test_domain/                # Domain-specific tests
    ├── test_llm/                   # LLM integration tests
    └── fixtures/                   # Test fixtures
```

This enhanced folder structure builds on the original design with several key improvements:

1. **Core Module Organization:**
   - `socialpulse/` contains all the main package code
   - Submodules organized by functionality with improved separation of concerns
   - New domain-specific modules for cryptocurrency-related functionality

2. **Enhanced GitLab Integration:**
   - Expanded GitLab connector with templates, workflows, and notification systems
   - Better structured for the human approval workflow via GitLab issues

3. **Think Window Implementation:**
   - Dedicated module for the 2-hour content refinement process
   - Includes scheduling, stage definition, and version control components

4. **LLM Integration:**
   - Structured approach to LLM integration with provider abstractions
   - Organized prompt management and fine-tuning capabilities
   - Token handling and optimization utilities

5. **Middleware Support:**
   - Dedicated middleware components for cross-cutting concerns
   - Authentication, rate limiting, and logging middleware

6. **Improved Monitoring:**
   - Comprehensive monitoring and observability system
   - Prometheus metrics, structured logging, and alerting
   - Dashboard definitions for visualization

7. **Configuration Management:**
   - Enhanced configuration system with versioning
   - Configuration migrations for managing changes
   - Validators for ensuring configuration integrity

8. **Documentation:**
   - Comprehensive documentation structure
   - API documentation, developer guides, and architecture diagrams
   - Usage examples for quick starts

9. **Expanded Testing:**
   - Additional test categories for domain-specific functionality and LLM integration
   - Broader coverage of the enhanced components

These improvements make the structure more robust, maintainable, and better aligned with the SocialPulse module's specific requirements for crypto content generation, human approval workflows, and the 2-hour content refinement process. The structure now better supports the entire dataflow from platform monitoring to human-approved posting.
