"""
Data validation module for URLs and publication data.
"""

import os
from urllib.parse import urlparse
from difflib import SequenceMatcher


def validate_url(url):
    """
    Validate that a URL is properly formed and accessible
    Returns tuple: (is_valid, cleaned_url, error_message)
    """
    if not url:
        return False, None, "URL is empty"

    # Basic cleanup
    url = url.strip()

    # Check if URL has a scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Parse URL
    try:
        parsed = urlparse(url)

        # Check for required components
        if not parsed.scheme or not parsed.netloc:
            return False, url, "Invalid URL format"

        # Check for valid scheme
        if parsed.scheme not in ["http", "https"]:
            return False, url, f"Invalid scheme: {parsed.scheme}"

        # Basic domain validation
        if "." not in parsed.netloc:
            return False, url, "Invalid domain"

        return True, url, None

    except Exception as e:
        return False, url, f"URL parsing error: {str(e)}"


def calculate_similarity(str1, str2):
    """
    Calculate similarity ratio between two strings (0.0 to 1.0)
    Uses SequenceMatcher for fuzzy matching
    """
    if not str1 or not str2:
        return 0.0

    # Normalize strings for comparison
    s1 = str1.lower().strip()
    s2 = str2.lower().strip()

    return SequenceMatcher(None, s1, s2).ratio()


def find_duplicates(publications, similarity_threshold=0.85):
    """
    Find potential duplicate publications based on name similarity
    Returns list of tuples: (index1, index2, similarity_score, pub1, pub2)
    """
    duplicates = []

    for i in range(len(publications)):
        for j in range(i + 1, len(publications)):
            pub1 = publications[i]
            pub2 = publications[j]

            # Compare names
            name_similarity = calculate_similarity(
                pub1.get("name", ""), pub2.get("name", "")
            )

            # Also compare URLs (exact match)
            same_url = (
                pub1.get("link") == pub2.get("link") and pub1.get("link") is not None
            )

            if name_similarity >= similarity_threshold or same_url:
                duplicates.append((i, j, name_similarity, pub1, pub2))

    return duplicates


def validate_publication_data(pub, strict=False):
    """
    Validate a publication data dictionary
    Returns tuple: (is_valid, errors, warnings)
    """
    errors = []
    warnings = []

    # Required fields
    if not pub.get("name"):
        errors.append("Missing required field: name")
    elif len(pub["name"].strip()) < 2:
        warnings.append(f"Publication name is very short: '{pub['name']}'")

    if not pub.get("link"):
        errors.append("Missing required field: link")
    else:
        is_valid, cleaned_url, error = validate_url(pub["link"])
        if not is_valid:
            errors.append(f"Invalid URL: {error}")
        elif cleaned_url != pub["link"]:
            warnings.append(f"URL cleaned from '{pub['link']}' to '{cleaned_url}'")
            pub["link"] = cleaned_url

    # Optional but recommended fields
    if not pub.get("author"):
        warnings.append("Missing author information")

    if "is_paid" not in pub:
        warnings.append("Missing payment status")

    # Validate icon path if present
    if pub.get("icon"):
        icon_path = pub["icon"]
        if not os.path.isabs(icon_path):
            warnings.append(f"Icon path is not absolute: {icon_path}")
        elif not os.path.exists(icon_path):
            warnings.append(f"Icon file does not exist: {icon_path}")

    # Check for suspicious data
    if pub.get("name") and len(pub["name"]) > 200:
        warnings.append(
            f"Publication name is unusually long ({len(pub['name'])} chars)"
        )

    # In strict mode, treat warnings as errors
    if strict:
        errors.extend(warnings)
        warnings = []

    is_valid = len(errors) == 0
    return is_valid, errors, warnings
