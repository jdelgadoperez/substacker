"""
Unified configuration module for the Substack scraper.

This module consolidates all configuration in one place:
- Environment variables (.env)
- Network settings (headers, timeouts)
- Performance settings (workers, caching)
- Feature flags
- Output paths
"""

import os
from pathlib import Path
from typing import Optional

# Load environment variables from .env file

try:
    from dotenv import load_dotenv

    # Load .env from the project root directory
    PROJECT_ROOT = Path(__file__).parent.parent
    env_path = PROJECT_ROOT / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # dotenv not installed, rely on system environment variables
    PROJECT_ROOT = Path(__file__).parent.parent


class Config:
    """
    Unified global configuration for the Substack scraper.

    All settings can be modified at runtime via CLI args or directly.
    Paths are derived from project root for portability.
    """

    # === Environment Variables (from .env) ===
    substack_user: str = os.getenv("SUBSTACK_USER", "")
    substack_cookie: str = os.getenv("SUBSTACK_COOKIE", "")

    # === Network Settings ===
    timeout: int = 10  # Request timeout in seconds
    max_retries: int = 2  # Number of retry attempts
    rate_limit_delay: float = 1.0  # Delay between requests in seconds

    # === Performance Settings ===
    max_workers: int = 5  # Concurrent download threads
    parallel_downloads: bool = True
    use_cache: bool = True
    skip_if_labeled: bool = True

    # === Feature Flags ===
    download_images: bool = True
    extract_metadata: bool = False
    validate_data: bool = True
    analyze_content: bool = True

    # === Output Paths (derived from project root) ===
    project_root: Path = PROJECT_ROOT
    images_folder: str = os.path.expanduser("~/projects/sandbox/exports/images")
    exports_folder: str = os.path.expanduser("~/projects/sandbox/exports")
    cache_dir: str = str(PROJECT_ROOT / ".cache")

    # === Label Filtering ===
    include_labels: Optional[list[str]] = (
        None  # None = all labels, or list of labels to include
    )
    exclude_labels: Optional[list[str]] = (
        None  # None = no exclusions, or list of labels to exclude
    )

    # === Cache Settings ===
    cache_expiry_days: int = 7  # Content cache expires after 7 days

    @classmethod
    def get_headers(cls) -> dict:
        """
        Generate HTTP headers for web scraping.

        Returns:
            dict: Headers including User-Agent and session cookie
        """
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Cookie": cls.substack_cookie,
        }

    @classmethod
    def get_substack_url(cls) -> str:
        """
        Generate the Substack reads URL from username.

        Returns:
            str: Full URL to user's reads page, or empty string if user not set
        """
        if not cls.substack_user:
            return ""

        # Ensure username starts with @
        username = cls.substack_user
        if not username.startswith("@"):
            username = f"@{username}"

        return f"https://substack.com/{username}/reads"

    @classmethod
    def validate(cls) -> list[str]:
        """
        Validate configuration and return list of issues.

        Returns:
            list[str]: List of validation error messages (empty if valid)
        """
        issues = []

        if not cls.substack_user:
            issues.append("SUBSTACK_USER not set in .env file")

        if not cls.substack_cookie:
            issues.append("SUBSTACK_COOKIE not set in .env file")

        if cls.max_workers < 1:
            issues.append(f"max_workers must be >= 1, got {cls.max_workers}")

        if cls.timeout < 1:
            issues.append(f"timeout must be >= 1, got {cls.timeout}")

        if cls.cache_expiry_days < 0:
            issues.append(
                f"cache_expiry_days must be >= 0, got {cls.cache_expiry_days}"
            )

        return issues


# Backward compatibility: Keep CACHE_EXPIRY_DAYS at module level
# This is deprecated, use Config.cache_expiry_days instead
CACHE_EXPIRY_DAYS = Config.cache_expiry_days
