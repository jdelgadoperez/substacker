"""
AI-powered labeling using Claude API.

This module provides cleaner, more accurate categorization than keyword-based
labeling by using Claude to understand publication context.
"""

import json
import os
from typing import Optional

from .logger import get_logger, ProgressBar

logger = get_logger(__name__)

# Simplified categories (12 vs 40+ in keyword labeling)
AI_CATEGORIES = [
    "Tech & Engineering",
    "Business & Startups",
    "Politics & Policy",
    "News & Current Events",
    "Social Justice & Identity",
    "Culture & Society",
    "Science & Climate",
    "Health & Wellness",
    "Law & Legal",
    "Religion & Spirituality",
    "Media & Entertainment",
    "Career & Leadership",
]

CATEGORIZATION_PROMPT = """You are categorizing newsletter subscriptions. Assign the most relevant categories that describe each publication's primary focus.

Categories:
- Tech & Engineering: Software, coding, system design, AI/ML, developer tools
- Business & Startups: Entrepreneurship, VC, business strategy, finance
- Politics & Policy: Government, elections, legislation, activism, democracy
- News & Current Events: Journalism, breaking news, daily briefings
- Social Justice & Identity: LGBTQ+, racial justice, intersectionality, civil rights
- Culture & Society: Pop culture, social commentary, lifestyle, trends
- Science & Climate: Research, environment, space, sustainability
- Health & Wellness: Medical, mental health, fitness, reproductive health
- Law & Legal: Legal analysis, courts, constitutional issues, lawyers
- Religion & Spirituality: Faith, deconstruction, theology, religious criticism
- Media & Entertainment: Film, TV, music, podcasts, streaming
- Career & Leadership: Professional development, management, workplace

Publications:
{publications_json}

Return a JSON array. Use your judgment on how many categories fit - some publications clearly focus on one topic, others genuinely span multiple areas. Assign 1-3 categories per publication.

Format: [{{"name": "Publication Name", "categories": ["Category1", "Category2"]}}, ...]

IMPORTANT: Return ONLY valid JSON, no markdown code blocks or extra text."""


def _get_anthropic_client():
    """Get Anthropic client, raising helpful error if not configured."""
    try:
        import anthropic
    except ImportError as err:
        raise ImportError(
            "anthropic package not installed. Run: uv add anthropic"
        ) from err

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable not set. "
            "Add it to your .env file."
        )

    return anthropic.Anthropic(api_key=api_key)


def _format_publication_for_prompt(publication: dict) -> dict:
    """Extract relevant fields for categorization prompt."""
    return {
        "name": publication.get("name", "Unknown"),
        "author": publication.get("author", ""),
        "description": publication.get("description", ""),
        "link": publication.get("link", ""),
    }


def _parse_claude_response(response_text: str) -> list[dict]:
    """Parse Claude's JSON response, handling potential formatting issues."""
    text = response_text.strip()

    # Remove markdown code blocks if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines (```json and ```)
        lines = [line for line in lines if not line.startswith("```")]
        text = "\n".join(lines)

    try:
        return json.loads(text)
    except json.JSONDecodeError as err:
        logger.error(f"Failed to parse Claude response: {err}")
        logger.debug(f"Raw response: {text[:500]}")
        return []


def _categorize_batch(
    client,
    publications: list[dict],
    model: str,
) -> dict[str, list[str]]:
    """
    Send a batch of publications to Claude for categorization.

    Returns:
        Dict mapping publication name to list of categories
    """
    formatted_pubs = [_format_publication_for_prompt(pub) for pub in publications]
    publications_json = json.dumps(formatted_pubs, indent=2)

    prompt = CATEGORIZATION_PROMPT.format(publications_json=publications_json)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = response.content[0].text
        parsed = _parse_claude_response(response_text)

        # Build name -> categories mapping
        result: dict[str, list[str]] = {}
        for item in parsed:
            name = item.get("name", "")
            categories = item.get("categories", [])
            # Validate categories are from our list
            valid_categories = [cat for cat in categories if cat in AI_CATEGORIES]
            if valid_categories:
                result[name] = valid_categories

        return result

    except Exception as err:
        logger.error(f"Claude API error: {err}")
        return {}


def categorize_with_claude(
    publications: list[dict],
    model: str = "claude-sonnet-4-20250514",
    skip_if_labeled: bool = True,
    batch_size: int = 15,
) -> list[dict]:
    """
    Categorize publications using Claude API.

    Args:
        publications: List of publication dicts with name, author, link, etc.
        model: Claude model to use
        skip_if_labeled: Skip publications that already have labels
        batch_size: Number of publications per API call

    Returns:
        Publications with updated labels
    """
    client = _get_anthropic_client()

    # Separate publications that need labeling
    to_label = []
    for pub in publications:
        if skip_if_labeled and pub.get("labels") and len(pub["labels"]) > 0:
            logger.debug(f"Skipping {pub.get('name', 'Unknown')} (already labeled)")
        else:
            to_label.append(pub)

    if not to_label:
        logger.info("All publications already labeled, skipping AI categorization")
        return publications

    logger.info(f"Categorizing {len(to_label)} publications with Claude ({model})")

    # Process in batches
    all_categories: dict[str, list[str]] = {}
    batches = [to_label[i : i + batch_size] for i in range(0, len(to_label), batch_size)]

    progress = ProgressBar(len(batches), "AI Labeling")

    for batch_num, batch in enumerate(batches, 1):
        logger.debug(f"Processing batch {batch_num}/{len(batches)} ({len(batch)} pubs)")
        batch_results = _categorize_batch(client, batch, model)
        all_categories.update(batch_results)
        progress.update(1, f"Batch {batch_num}/{len(batches)}")

    # Apply categories back to publications
    labeled_count = 0
    for pub in publications:
        name = pub.get("name", "")
        if name in all_categories:
            pub["labels"] = all_categories[name]
            labeled_count += 1
            logger.debug(f"{name}: {pub['labels']}")

    logger.info(f"Labeled {labeled_count} publications")

    return publications
