"""
Cache management module for content analysis results.
"""

import os
import hashlib
import pickle
from datetime import datetime, timedelta
from .config import Config, CACHE_EXPIRY_DAYS
from .logger import get_logger

logger = get_logger(__name__)


def get_cache_key(url):
    """Generate a cache key from a URL"""
    return hashlib.md5(url.encode()).hexdigest()


def get_cached_metadata(url, cache_dir=None):
    """
    Retrieve cached metadata for a URL if it exists and is not expired
    Returns None if cache miss or expired
    """
    if cache_dir is None:
        cache_dir = Config.cache_dir

    if not os.path.exists(cache_dir):
        return None

    cache_key = get_cache_key(url)
    cache_file = os.path.join(cache_dir, f"{cache_key}.pkl")

    if not os.path.exists(cache_file):
        return None

    try:
        with open(cache_file, "rb") as f:
            cached_data = pickle.load(f)

        # Check if cache is expired
        cache_time = cached_data.get("timestamp")
        if cache_time:
            age = datetime.now() - cache_time
            if age > timedelta(days=CACHE_EXPIRY_DAYS):
                return None

        return cached_data.get("metadata")

    except Exception as e:
        logger.debug(f"Error reading cache: {e}")
        return None


def save_cached_metadata(url, metadata, cache_dir=None):
    """Save metadata to cache"""
    if cache_dir is None:
        cache_dir = Config.cache_dir

    try:
        os.makedirs(cache_dir, exist_ok=True)

        cache_key = get_cache_key(url)
        cache_file = os.path.join(cache_dir, f"{cache_key}.pkl")

        cached_data = {"timestamp": datetime.now(), "url": url, "metadata": metadata}

        with open(cache_file, "wb") as f:
            pickle.dump(cached_data, f)

    except Exception as e:
        logger.debug(f"Error writing cache: {e}")


def clear_cache(cache_dir=None):
    """Clear the content analysis cache"""
    if cache_dir is None:
        cache_dir = Config.cache_dir

    if os.path.exists(cache_dir):
        import shutil

        shutil.rmtree(cache_dir)
        logger.info(f"Cleared cache directory: {cache_dir}")
        return True
    else:
        logger.info(f"No cache directory found at: {cache_dir}")
        return False
