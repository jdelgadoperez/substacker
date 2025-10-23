"""
Auto-labeling and label filtering module.
"""

import re
from urllib.parse import urlparse
from .cache import get_cached_metadata
from .metadata import analyze_publication_content
from .logger import get_logger, ProgressBar

logger = get_logger(__name__)


def extract_url_keywords(url):
    """Extract potential keywords from URL structure"""
    if not url:
        return []

    parsed = urlparse(url.lower())
    domain_parts = parsed.netloc.split('.')
    path_parts = parsed.path.strip('/').split('/')

    keywords = []
    for part in domain_parts + path_parts:
        # Remove common TLDs and subdomains
        if part not in ['www', 'com', 'org', 'net', 'substack', 'io', 'co']:
            keywords.append(part)

    return keywords


def word_boundary_search(text, keyword):
    """Search for keyword with word boundaries to avoid partial matches"""
    # Escape special regex characters in keyword
    escaped_keyword = re.escape(keyword)
    # Use word boundaries (\b) for single words, looser matching for phrases
    if ' ' in keyword:
        # For phrases, just check if it exists as-is
        pattern = r'\b' + escaped_keyword.replace(r'\ ', r'\s+') + r'\b'
    else:
        pattern = r'\b' + escaped_keyword + r'\b'

    return bool(re.search(pattern, text, re.IGNORECASE))


def calculate_category_score(category, keywords, text_sources):
    """Calculate weighted score for a category based on where keywords match"""
    score = 0
    matches = []

    name_text = text_sources.get('name', '').lower()
    author_text = text_sources.get('author', '').lower()
    url_text = ' '.join(text_sources.get('url_keywords', [])).lower()
    content_text = text_sources.get('content', '').lower()
    author_bio_text = text_sources.get('author_bio', '').lower()

    for keyword in keywords:
        keyword_lower = keyword.lower()

        # Highest-value matches: known author bio (verified information)
        if author_bio_text and word_boundary_search(author_bio_text, keyword_lower):
            score += 4
            matches.append(f"{keyword} in author bio")

        # High-value matches: name and URL
        if word_boundary_search(name_text, keyword_lower):
            score += 3
            matches.append(f"{keyword} in name")

        if word_boundary_search(url_text, keyword_lower):
            score += 2
            matches.append(f"{keyword} in URL")

        # Medium-value matches: author
        if word_boundary_search(author_text, keyword_lower):
            score += 1
            matches.append(f"{keyword} in author")

        # Lower-value matches: content (but still valuable)
        if content_text and word_boundary_search(content_text, keyword_lower):
            score += 1.5
            matches.append(f"{keyword} in content")

    return score, matches


def auto_label_publications(
    publications, analyze_content=True, skip_if_labeled=True, use_cache=True
):
    """Automatically assign labels based on publication characteristics"""
    from definitions import KEYWORD_CATEGORIES, KNOWN_AUTHORS

    progress = ProgressBar(len(publications), "Labeling")

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

        # Prepare text sources dictionary
        text_sources = {
            'name': pub.get("name", ""),
            'author': pub.get("author", ""),
            'url_keywords': extract_url_keywords(pub.get("link", "")),
            'content': "",
            'author_bio': ""
        }

        # Check for known author information
        author_name = pub.get("author", "").lower().strip()
        if author_name in KNOWN_AUTHORS:
            text_sources['author_bio'] = " ".join(KNOWN_AUTHORS[author_name])
            logger.debug(f"  Found known author: {author_name} → {text_sources['author_bio']}")
        else:
            # Try first name only as fallback
            first_name = author_name.split()[0] if author_name else ""
            if first_name and first_name in KNOWN_AUTHORS:
                text_sources['author_bio'] = " ".join(KNOWN_AUTHORS[first_name])
                logger.debug(f"  Found known author by first name: {first_name} → {text_sources['author_bio']}")

        # Add content analysis if enabled
        if analyze_content and pub.get("link"):
            cached_metadata = get_cached_metadata(pub["link"]) if use_cache else None
            if cached_metadata:
                logger.debug(f"Using cached content analysis")
                text_sources['content'] = cached_metadata.get("content_text", "")
            else:
                logger.debug(f"Fetching content from {pub['link']}...")
                text_sources['content'] = analyze_publication_content(pub["link"])

            if text_sources['content']:
                logger.debug(f"Content analyzed ({len(text_sources['content'])} chars)")
            else:
                logger.debug(f"Could not analyze content")

        # Calculate scores for each category
        category_scores = {}
        for category, keywords in KEYWORD_CATEGORIES.items():
            score, matches = calculate_category_score(category, keywords, text_sources)
            if score > 0:
                category_scores[category] = {'score': score, 'matches': matches}
                logger.debug(f"  {category}: score={score:.1f}, matches={matches[:3]}")

        # Apply labels based on score thresholds
        for category, data in category_scores.items():
            score = data['score']
            # Lower threshold: any match gets a label
            if score >= 1:
                labels.append(category)
            # Higher threshold for "focused" designation
            if score >= 5:
                labels.append(f"{category}-focused")

        # Fallback strategies for publications with few/no labels
        if len(labels) <= 1:  # Only has free/paid label
            logger.debug(f"  Applying fallback strategies (current labels: {labels})")

            # Strategy 1: Infer from publication name patterns
            name_lower = pub.get("name", "").lower()
            author_lower = pub.get("author", "").lower()

            # Check for personal newsletters (name matches author)
            if author_lower and name_lower:
                if author_lower in name_lower:
                    labels.append("writing")
                    logger.debug(f"  Fallback: Added 'writing' (personal newsletter)")

            # Strategy 2: Check for title-only publications (often opinion/commentary)
            if not author_lower or author_lower == name_lower:
                labels.append("writing")
                logger.debug(f"  Fallback: Added 'writing' (single-author format)")

            # Strategy 3: Contextual name inference
            if "objection" in name_lower or "lawyer" in name_lower or "legal" in name_lower:
                labels.append("law")
                logger.debug(f"  Fallback: Added 'law' from name context")

            if "music" in name_lower or "band" in name_lower or "song" in name_lower:
                labels.append("music")
                logger.debug(f"  Fallback: Added 'music' from name context")

            # Check for possessive names (often personal commentary)
            if "'s " in name_lower or "by" in name_lower:
                if "law" not in labels and "music" not in labels:
                    labels.append("writing")
                    logger.debug(f"  Fallback: Added 'writing' (possessive format)")

            # Strategy 4: URL pattern inference
            url_keywords = text_sources.get('url_keywords', [])
            for kw in url_keywords:
                if len(kw) > 3:  # Avoid short meaningless strings
                    # Check if URL keyword suggests a category
                    if kw in ['tech', 'code', 'dev', 'engineering']:
                        labels.append("tech")
                        logger.debug(f"  Fallback: Added 'tech' from URL ({kw})")
                    elif kw in ['news', 'daily', 'weekly', 'newsletter']:
                        labels.append("news")
                        logger.debug(f"  Fallback: Added 'news' from URL ({kw})")
                    elif kw in ['music', 'band', 'album']:
                        labels.append("music")
                        logger.debug(f"  Fallback: Added 'music' from URL ({kw})")
                    elif kw in ['objection', 'legal', 'lawyer']:
                        labels.append("law")
                        logger.debug(f"  Fallback: Added 'law' from URL ({kw})")

        pub["labels"] = sorted(list(set(labels)))
        logger.debug(f"Final labels: {', '.join(pub['labels'])}")
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
