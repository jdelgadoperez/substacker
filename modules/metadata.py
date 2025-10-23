"""
Metadata extraction module for analyzing publication content.
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from .cache import get_cached_metadata, save_cached_metadata
from .config import Config
from .logger import get_logger

logger = get_logger(__name__)


def search_author_info(author_name, publication_name=""):
    """
    Search for author information using web search as fallback.
    Returns a brief bio/description if found.
    """
    if not author_name or len(author_name) < 3:
        return ""

    try:
        # Try Wikipedia/public info search
        search_query = f"{author_name} {publication_name} bio" if publication_name else f"{author_name} who is"

        # For now, we'll use a simple approach - try to fetch from a search
        # In production, you could use Google Custom Search API or similar
        logger.debug(f"Would search for: {search_query}")

        # TODO: Implement actual web search here if needed
        # For now, return empty to avoid making external API calls
        return ""

    except Exception as e:
        logger.debug(f"Error searching for author info: {e}")
        return ""


def extract_metadata(
    url, max_retries=None, timeout=None, rate_limit_delay=None, use_cache=True
):
    """
    Extract rich metadata from a publication's home page
    Returns dict with: description, subscriber_info, post_count, content_text
    """
    # Use config defaults if not specified
    if max_retries is None:
        max_retries = Config.max_retries
    if timeout is None:
        timeout = Config.timeout
    if rate_limit_delay is None:
        rate_limit_delay = Config.rate_limit_delay

    # Check cache first
    if use_cache:
        cached = get_cached_metadata(url)
        if cached:
            return cached

    # Import headers from parent
    from definitions import HEADERS

    metadata = {
        "description": "",
        "subscriber_info": "",
        "post_count": None,
        "content_text": "",
        "about_text": "",
    }

    for attempt in range(max_retries):
        try:
            time.sleep(rate_limit_delay)
            response = requests.get(url, headers=HEADERS, timeout=timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract meta description
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                metadata["description"] = meta_desc["content"].strip()

            if not metadata["description"]:
                og_desc = soup.find("meta", property="og:description")
                if og_desc and og_desc.get("content"):
                    metadata["description"] = og_desc["content"].strip()

            # Extract subscriber information
            subscriber_patterns = [
                (r"(\d+[,\d]*)\s+subscribers?", "subscribers"),
                (r"(\d+[,\d]*)\s+readers?", "readers"),
                (r"(\d+[KkMm])\s+subscribers?", "subscribers"),
            ]

            page_text = soup.get_text()
            for pattern, label in subscriber_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    metadata["subscriber_info"] = f"{match.group(1)} {label}"
                    break

            # Extract about section
            about_keywords = ["about", "about this publication", "about the author"]
            for keyword in about_keywords:
                heading = soup.find(
                    ["h1", "h2", "h3", "h4"], string=re.compile(keyword, re.IGNORECASE)
                )
                if heading:
                    about_text = []
                    for sibling in heading.find_next_siblings(["p", "div"]):
                        text = sibling.get_text(strip=True)
                        if text:
                            about_text.append(text)
                        if len(about_text) >= 3:
                            break
                    if about_text:
                        metadata["about_text"] = " ".join(about_text)[:500]
                        break

            # Extract content text for keyword analysis
            content_text = ""
            title = soup.find("title")
            if title:
                content_text += f" {title.get_text()} "
            if metadata["description"]:
                content_text += f" {metadata['description']} "
            if metadata["about_text"]:
                content_text += f" {metadata['about_text']} "

            content_selectors = [
                "article",
                ".post-content",
                ".entry-content",
                '[class*="post"]',
                "main",
                ".content",
            ]
            for selector in content_selectors:
                elements = soup.select(selector)
                for elem in elements[:3]:
                    text = elem.get_text(strip=True, separator=" ")
                    content_text += f" {text[:500]} "
                    break

            if len(content_text.strip()) < 100:
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                body_text = soup.get_text(strip=True, separator=" ")
                content_text += f" {body_text[:1000]} "

            metadata["content_text"] = content_text.lower()

            # Save to cache
            if use_cache:
                save_cached_metadata(url, metadata)

            return metadata

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                logger.debug(f"Timeout, retrying ({attempt + 1}/{max_retries})...")
                continue
            else:
                logger.warning(f"Timeout after {max_retries} attempts for {url}")
        except Exception as e:
            logger.error(f"Error extracting metadata from {url}: {e}")
            break

    return metadata


def analyze_publication_content(url, max_retries=2):
    """
    Fetch and analyze the first page of a publication for better labeling
    Returns extracted text content for keyword analysis
    (Deprecated: Use extract_metadata() for richer data extraction)
    """
    metadata = extract_metadata(url, max_retries)
    return metadata.get("content_text", "")
