"""
Data export module for CSV and JSON output.
"""

import os
import json
import csv


def save_to_csv(data, filename="exports/substack_reads.csv"):
    """Save the scraped data to a CSV file"""
    if not data:
        print("No data to save")
        return

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


def save_to_json(data, filename="exports/substack_reads.json"):
    """Save the scraped data to a JSON file"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ Data saved to {filename}")
