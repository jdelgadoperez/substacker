"""
Core scraping module for extracting publication data from Substack.
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse

from .validation import validate_publication_data
from .downloads import sanitize_filename, download_images_parallel
from .metadata import extract_metadata
from .logger import get_logger, ProgressBar
from .config import Config

logger = get_logger(__name__)


def scrape_substack_reads(
    url,
    download_images=True,
    images_folder=None,
    extract_rich_metadata=False,
    validate_data=True,
    parallel_downloads=True,
    max_workers=None,
):
    """
    Scrape a Substack reads page to extract publication data
    """
    # Use Config defaults if not provided
    if images_folder is None:
        images_folder = Config.images_folder
    if max_workers is None:
        max_workers = Config.max_workers

    if download_images:
        Path(images_folder).mkdir(parents=True, exist_ok=True)

    try:
        response = requests.get(url, headers=Config.get_headers())
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        publications = []
        skipped_count = 0
        image_tasks = []

        pub_links = soup.find_all("a", class_=re.compile(r"readsRow-\w+"))
        logger.info(f"Found {len(pub_links)} potential publications to scrape")

        # Progress bar for extraction
        progress = ProgressBar(len(pub_links), "Extracting")

        # First pass: Extract all data
        for i, link in enumerate(pub_links, 1):
            pub_data = {}

            if link.get("href"):
                pub_data["link"] = link["href"]

            name_elem = link.find("div", class_=re.compile(r"weight-semibold-\w+"))
            if name_elem:
                pub_data["name"] = name_elem.get_text(strip=True)

            author_elem = link.find("div", class_=re.compile(r"weight-regular-\w+"))
            if author_elem:
                author_text = author_elem.get_text(strip=True)
                # Remove "by " prefix if present
                pub_data["author"] = author_text.replace("by ", "", 1).strip()

            icon_elem = link.find("img")
            if icon_elem and icon_elem.get("src"):
                og_icon = icon_elem["src"]

                if download_images and pub_data.get("name"):
                    clean_name = sanitize_filename(pub_data["name"])
                    parsed_url = urlparse(og_icon)
                    url_filename = os.path.basename(parsed_url.path)
                    extension = (
                        os.path.splitext(url_filename)[1]
                        if "." in url_filename
                        else ".jpg"
                    )
                    filename = f"{clean_name}{extension}"

                    pub_data["_image_task"] = (og_icon, images_folder, filename)
                    image_tasks.append((og_icon, images_folder, filename))

            image_container = link.find(
                "div", class_=re.compile(r"pc-display-flex pc-position-relative")
            )
            is_paid = False
            if image_container:
                svg_badge = image_container.find("svg", class_=re.compile(r"badge-\w+"))
                is_paid = svg_badge is not None
            pub_data["is_paid"] = is_paid

            # Extract rich metadata if requested
            if extract_rich_metadata and pub_data.get("link"):
                logger.debug(
                    f"Extracting metadata for {pub_data.get('name', 'Unknown')}..."
                )
                metadata = extract_metadata(pub_data["link"])
                if metadata.get("description"):
                    pub_data["description"] = metadata["description"]
                if metadata.get("subscriber_info"):
                    pub_data["subscriber_info"] = metadata["subscriber_info"]
                if metadata.get("about_text"):
                    pub_data["about_text"] = metadata["about_text"]

            # Validate data before adding
            if validate_data:
                is_valid, errors, warnings = validate_publication_data(pub_data)

                if not is_valid:
                    logger.warning(
                        f"Skipping invalid publication: {pub_data.get('name', 'Unknown')}"
                    )
                    for error in errors:
                        logger.debug(f"  Validation error: {error}")
                    skipped_count += 1
                    progress.update(
                        1, f"Skipped: {pub_data.get('name', 'Unknown')[:30]}"
                    )
                    continue

                if warnings:
                    logger.debug(
                        f"Warnings for {pub_data.get('name', 'Unknown')}: {', '.join(warnings)}"
                    )

            if pub_data.get("name") and pub_data.get("link"):
                publications.append(pub_data)
                progress.update(1, f"{pub_data.get('name', 'Unknown')[:30]}")

        # Download images in parallel if enabled
        if download_images and image_tasks:
            if parallel_downloads and len(image_tasks) > 1:
                logger.info(
                    f"Downloading {len(image_tasks)} images in parallel (max {max_workers} workers)..."
                )
                image_results = download_images_parallel(image_tasks, max_workers)

                cached_count = 0
                downloaded_count = 0
                for idx, pub in enumerate(publications):
                    if "_image_task" in pub:
                        if idx in image_results:
                            file_path, was_cached = image_results[idx]
                            if file_path:
                                pub["icon"] = os.path.abspath(file_path)
                                if was_cached:
                                    cached_count += 1
                                else:
                                    downloaded_count += 1
                        del pub["_image_task"]

                logger.info(
                    f"Images: {cached_count} cached, {downloaded_count} newly downloaded"
                )
            else:
                from .downloads import download_image

                logger.info(f"Downloading {len(image_tasks)} images sequentially...")
                download_progress = ProgressBar(len(image_tasks), "Downloading images")
                for idx, pub in enumerate(publications):
                    if "_image_task" in pub:
                        url, folder, filename = pub["_image_task"]
                        file_path, was_cached = download_image(
                            url, folder, filename, True
                        )
                        if file_path:
                            pub["icon"] = os.path.abspath(file_path)
                            status = "cached" if was_cached else "downloaded"
                            download_progress.update(1, f"{status}: {pub['name'][:30]}")
                        del pub["_image_task"]

        logger.info(f"Successfully scraped {len(publications)} publications")
        if skipped_count > 0:
            logger.warning(f"Skipped {skipped_count} invalid publications")

        return publications

    except requests.RequestException as e:
        logger.error(f"Error fetching the page: {e}")
        return []
    except Exception as e:
        logger.error(f"Error parsing the page: {e}")
        return []
