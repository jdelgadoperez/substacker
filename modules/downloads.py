"""
Image download module with parallel and sequential support.
"""

import os
import re
import unicodedata
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from .logger import get_logger

logger = get_logger(__name__)


def sanitize_filename(filename):
    """Sanitize filename for filesystem compatibility"""
    if not filename:
        return "unnamed_file"

    filename = unicodedata.normalize("NFKD", filename)
    filename = re.sub(r"[^\w\-_\.]", "_", filename)
    filename = re.sub(r"_{2,}", "_", filename)
    filename = filename.strip("_.")

    if not filename or filename.isspace():
        filename = "unnamed_file"

    max_length = 200
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[: max_length - len(ext) - 10] + ext

    return filename


def download_image(url, folder_path, filename=None, skip_if_exists=True):
    """Download an image from URL - Returns tuple (file_path, was_cached)"""
    from definitions import HEADERS

    try:
        if not filename:
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if "." not in filename:
                filename += ".jpg"

        filename = sanitize_filename(filename)
        file_path = os.path.join(folder_path, filename)

        if skip_if_exists and os.path.exists(file_path):
            if os.path.getsize(file_path) > 0:
                return file_path, True
            else:
                os.remove(file_path)

        response = requests.get(url, headers=HEADERS, stream=True, timeout=10)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return file_path, False

    except Exception as e:
        logger.debug(f"Error downloading image {url}: {e}")
        return None, False


def download_images_parallel(image_tasks, max_workers=5):
    """Download multiple images in parallel - Returns dict mapping index to (file_path, was_cached)"""
    results = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(download_image, url, folder, filename, True): idx
            for idx, (url, folder, filename) in enumerate(image_tasks)
        }

        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                result = future.result()
                results[idx] = result
            except Exception as e:
                logger.debug(f"Error in parallel download: {e}")
                results[idx] = (None, False)

    return results
