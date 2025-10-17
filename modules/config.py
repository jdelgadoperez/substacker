"""
Configuration module for the Substack scraper.
"""

# Cache configuration
CACHE_DIR = ".cache"
CACHE_EXPIRY_DAYS = 7  # Content cache expires after 7 days


class Config:
    """Global configuration for the scraper"""

    # Network settings
    timeout = 10  # Request timeout in seconds
    max_retries = 2  # Number of retry attempts
    rate_limit_delay = 1.0  # Delay between requests in seconds

    # Performance settings
    max_workers = 5  # Concurrent download threads
    parallel_downloads = True
    use_cache = True
    skip_if_labeled = True

    # Feature flags
    download_images = True
    extract_metadata = False
    validate_data = True
    analyze_content = True

    # Output settings
    images_folder = "images"
    exports_folder = "exports"

    # Label filtering
    include_labels = None  # None = all labels, or list of labels to include
    exclude_labels = None  # None = no exclusions, or list of labels to exclude
