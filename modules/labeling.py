"""
Auto-labeling and label filtering module.
"""

from .cache import get_cached_metadata
from .metadata import analyze_publication_content
from .logger import get_logger, ProgressBar

logger = get_logger(__name__)


def auto_label_publications(
    publications, analyze_content=True, skip_if_labeled=True, use_cache=True
):
    """Automatically assign labels based on publication characteristics"""
    from definitions import KEYWORD_CATEGORIES

    progress = ProgressBar(len(publications), "Labeling publications")

    for i, pub in enumerate(publications, 1):
        if skip_if_labeled and pub.get("labels") and len(pub["labels"]) > 0:
            logger.debug(f"Skipping {pub.get('name', 'Unknown')} (already labeled)")
            progress.update(1, f"Skipped: {pub.get('name', 'Unknown')[:30]}")
            continue

        labels = []
        logger.debug(f"Analyzing publication: {pub.get('name', 'Unknown')}")

        # Label based on payment status
        if pub.get("is_paid"):
            labels.append("paid")
        else:
            labels.append("free")

        # Label based on subscription status
        status = pub.get("subscription_status", "").lower()
        if "subscribed" in status:
            labels.append("subscribed")
        elif "follow" in status:
            labels.append("following")
        elif "unsubscribed" in status:
            labels.append("unsubscribed")

        # Combine text sources for analysis
        text_sources = [pub.get("name", ""), pub.get("author", "")]

        # Add content analysis if enabled
        if analyze_content and pub.get("link"):
            cached_metadata = get_cached_metadata(pub["link"]) if use_cache else None
            if cached_metadata:
                logger.debug(f"Using cached content analysis")
                content_text = cached_metadata.get("content_text", "")
            else:
                logger.debug(f"Fetching content from {pub['link']}...")
                content_text = analyze_publication_content(pub["link"])

            if content_text:
                text_sources.append(content_text)
                logger.debug(f"Content analyzed ({len(content_text)} chars)")
            else:
                logger.debug(f"Could not analyze content")

        # Combine all text for keyword matching
        combined_text = " ".join(text_sources).lower()

        # Check against each category
        for category, keywords in KEYWORD_CATEGORIES.items():
            matches = sum(1 for keyword in keywords if keyword in combined_text)
            if matches >= 1:
                labels.append(category)
                if matches >= 3:
                    labels.append(f"{category}-focused")

        # Add priority label for paid subscriptions you're actually subscribed to
        if pub.get("is_paid") and "subscribed" in labels:
            labels.append("premium")

        pub["labels"] = sorted(list(set(labels)))
        logger.debug(f"Labels: {', '.join(pub['labels'])}")
        progress.update(1, f"{pub.get('name', 'Unknown')[:30]}")

    return publications


def filter_labels(publications, include_labels=None, exclude_labels=None):
    """Filter publication labels based on include/exclude lists"""
    if not include_labels and not exclude_labels:
        return publications

    for pub in publications:
        if "labels" in pub and pub["labels"]:
            original_labels = pub["labels"]

            if include_labels:
                pub["labels"] = [l for l in pub["labels"] if l in include_labels]
            if exclude_labels:
                pub["labels"] = [l for l in pub["labels"] if l not in exclude_labels]

            if len(pub["labels"]) != len(original_labels):
                removed = set(original_labels) - set(pub["labels"])
                logger.debug(
                    f"Filtered {pub.get('name', 'Unknown')}: removed {removed}"
                )

    return publications
