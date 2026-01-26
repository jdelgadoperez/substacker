"""
Data export module for CSV, JSON, and OPML output.
"""

import os
import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from xml.dom import minidom
from .config import Config


def save_to_csv(data, filename=None):
    """Save the scraped data to a CSV file"""
    if not data:
        print("No data to save")
        return

    if filename is None:
        filename = os.path.join(Config.exports_folder, "substack_reads.csv")

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Collect all unique keys
    all_keys = set()
    for row in data:
        all_keys.update(row.keys())

    # Define preferred order
    preferred_order = [
        "name",
        "author",
        "link",
        "rss_url",
        "description",
        "subscriber_info",
        "about_text",
        "icon",
        "is_paid",
        "subscription_status",
        "labels",
    ]

    fieldnames = [field for field in preferred_order if field in all_keys]
    fieldnames.extend(sorted(all_keys - set(fieldnames)))

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            csv_row = row.copy()
            for key, value in csv_row.items():
                if isinstance(value, list):
                    csv_row[key] = ", ".join(str(v) for v in value)
            writer.writerow(csv_row)
    print(f"✓ Data saved to {filename}")


def save_to_json(data, filename=None):
    """Save the scraped data to a JSON file"""
    if filename is None:
        filename = os.path.join(Config.exports_folder, "substack_reads.json")

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ Data saved to {filename}")


def save_to_opml(data, filename=None):
    """
    Save the scraped data to an OPML file for feed reader import.

    OPML 2.0 format compatible with Feedly, Inoreader, NetNewsWire, FreshRSS, etc.
    Groups feeds by label/category when available.

    Args:
        data: List of publication dictionaries with rss_url field
        filename: Output filename (default: substack_feeds.opml in exports folder)
    """
    if not data:
        print("No data to save")
        return

    if filename is None:
        filename = os.path.join(Config.exports_folder, Config.opml_filename)

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Filter to only publications with RSS URLs
    feeds = [pub for pub in data if pub.get("rss_url")]

    if not feeds:
        print("No publications with RSS URLs to export")
        return

    # Create OPML structure
    opml = ET.Element("opml", version="2.0")

    # Head section
    head = ET.SubElement(opml, "head")
    ET.SubElement(head, "title").text = "Substack Subscriptions"
    ET.SubElement(head, "dateCreated").text = datetime.now().strftime(
        "%a, %d %b %Y %H:%M:%S %z"
    )
    ET.SubElement(head, "docs").text = "http://opml.org/spec2.opml"

    # Body section
    body = ET.SubElement(opml, "body")

    # Group feeds by labels
    categorized = {}
    uncategorized = []

    for pub in feeds:
        labels = pub.get("labels", [])
        if labels:
            # Use first label as primary category
            primary_label = labels[0] if isinstance(labels, list) else labels
            if primary_label not in categorized:
                categorized[primary_label] = []
            categorized[primary_label].append(pub)
        else:
            uncategorized.append(pub)

    def create_outline(parent, pub):
        """Create an outline element for a publication."""
        outline = ET.SubElement(
            parent,
            "outline",
            type="rss",
            text=pub.get("name", "Unknown"),
            title=pub.get("name", "Unknown"),
            xmlUrl=pub.get("rss_url", ""),
            htmlUrl=pub.get("link", ""),
        )
        # Add description if available
        if pub.get("description"):
            outline.set("description", pub["description"])
        return outline

    # Add categorized feeds
    for label in sorted(categorized.keys()):
        category_outline = ET.SubElement(
            body, "outline", text=label.title(), title=label.title()
        )
        for pub in categorized[label]:
            create_outline(category_outline, pub)

    # Add uncategorized feeds
    if uncategorized:
        if categorized:
            # Only create "Uncategorized" folder if there are other categories
            uncategorized_outline = ET.SubElement(
                body, "outline", text="Uncategorized", title="Uncategorized"
            )
            for pub in uncategorized:
                create_outline(uncategorized_outline, pub)
        else:
            # No categories at all, add directly to body
            for pub in uncategorized:
                create_outline(body, pub)

    # Pretty print XML
    xml_str = ET.tostring(opml, encoding="unicode")
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent="  ")

    # Remove extra blank lines and XML declaration formatting issues
    lines = [line for line in pretty_xml.split("\n") if line.strip()]
    pretty_xml = "\n".join(lines)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print(f"✓ OPML saved to {filename} ({len(feeds)} feeds)")
