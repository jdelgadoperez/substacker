# definitions.py

import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env from the script's directory
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # dotenv not installed, rely on system environment variables
    pass


# HTTP headers for web scraping
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Cookie": os.getenv("SUBSTACK_COOKIE", ""),  # Load from environment variable
}

# Target URL - dynamically generated from SUBSTACK_USER
SUBSTACK_USER = os.getenv("SUBSTACK_USER", "")
if SUBSTACK_USER:
    # Ensure username starts with @
    if not SUBSTACK_USER.startswith("@"):
        SUBSTACK_USER = f"@{SUBSTACK_USER}"
    SUBSTACK_URL = f"https://substack.com/{SUBSTACK_USER}/reads"
else:
    # Fallback if SUBSTACK_USER not set
    SUBSTACK_URL = ""

# Keyword categories for auto-labeling
KEYWORD_CATEGORIES = {
    "tech": [
        "tech",
        "ai",
        "software",
        "coding",
        "programming",
        "data",
        "developer",
        "machine learning",
        "startup",
        "saas",
        "api",
        "cloud",
        "crypto",
        "blockchain",
        "devops",
    ],
    "business": [
        "business",
        "finance",
        "marketing",
        "economy",
        "investing",
        "money",
        "entrepreneur",
        "leadership",
        "strategy",
        "growth",
        "revenue",
    ],
    "news": [
        "news",
        "current events",
        "breaking",
        "daily",
        "weekly",
        "report",
        "dispatch",
        "briefing",
        "update",
        "headlines",
        "today",
        "morning",
        "evening",
        "times",
        "post",
        "herald",
        "tribune",
        "journal",
        "gazette",
        "chronicle",
        "observer",
        "reporter",
        "correspondent",
        "journalism",
        "journalist",
        "newsroom",
        "press",
        "wire",
        "bulletin",
        "alert",
        "digest",
        "roundup",
        "wrap",
        "recap",
        "summary",
        "international",
        "global",
        "world",
        "national",
        "local",
        "regional",
    ],
    "politics": [
        "politics",
        "policy",
        "government",
        "election",
        "democracy",
        "law",
        "congress",
        "senate",
        "political",
        "campaign",
        "voting",
        "ballot",
        "republican",
        "democrat",
        "conservative",
        "liberal",
        "progressive",
    ],
    "writing": [
        "writing",
        "newsletter",
        "content",
        "journalism",
        "media",
        "publishing",
        "storytelling",
        "blog",
        "author",
        "editor",
    ],
    "culture": [
        "culture",
        "art",
        "music",
        "film",
        "book",
        "literature",
        "entertainment",
        "pop culture",
        "celebrity",
        "review",
    ],
    "health": [
        "health",
        "wellness",
        "fitness",
        "mental health",
        "medical",
        "nutrition",
        "psychology",
        "therapy",
        "mindfulness",
    ],
    "science": [
        "science",
        "research",
        "climate",
        "environment",
        "physics",
        "biology",
        "chemistry",
        "space",
        "nature",
        "study",
    ],
}

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
