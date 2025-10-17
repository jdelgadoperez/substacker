"""
Data quality reporting module.
"""

from .validation import validate_publication_data


def generate_data_quality_report(publications):
    """Generate a comprehensive data quality report"""
    report = {
        "total_publications": len(publications),
        "complete_fields": {},
        "missing_fields": {},
        "field_coverage": {},
        "validation_summary": {"valid": 0, "warnings": 0, "errors": 0},
        "payment_breakdown": {"paid": 0, "free": 0, "unknown": 0},
    }

    all_fields = set()
    for pub in publications:
        all_fields.update(pub.keys())

    for field in all_fields:
        present_count = sum(1 for pub in publications if pub.get(field))
        report["complete_fields"][field] = present_count
        report["missing_fields"][field] = len(publications) - present_count
        report["field_coverage"][field] = (
            (present_count / len(publications) * 100) if publications else 0
        )

    for pub in publications:
        is_valid, errors, warnings = validate_publication_data(pub)
        if is_valid:
            report["validation_summary"]["valid"] += 1
        if errors:
            report["validation_summary"]["errors"] += 1
        if warnings:
            report["validation_summary"]["warnings"] += 1

        if "is_paid" in pub:
            if pub["is_paid"]:
                report["payment_breakdown"]["paid"] += 1
            else:
                report["payment_breakdown"]["free"] += 1
        else:
            report["payment_breakdown"]["unknown"] += 1

    return report


def print_data_quality_report(report):
    """Print a formatted data quality report"""
    print("\n" + "=" * 60)
    print("DATA QUALITY REPORT")
    print("=" * 60)

    print(f"\nTotal Publications: {report['total_publications']}")

    print("\n--- Payment Breakdown ---")
    paid = report["payment_breakdown"]["paid"]
    free = report["payment_breakdown"]["free"]
    unknown = report["payment_breakdown"]["unknown"]
    total = report["total_publications"]
    print(f"  Paid:    {paid:3d} ({paid/total*100:.1f}%)")
    print(f"  Free:    {free:3d} ({free/total*100:.1f}%)")
    if unknown > 0:
        print(f"  Unknown: {unknown:3d} ({unknown/total*100:.1f}%)")

    print("\n--- Field Coverage ---")
    key_fields = [
        "name",
        "link",
        "author",
        "icon",
        "is_paid",
        "description",
        "labels",
    ]
    for field in key_fields:
        if field in report["field_coverage"]:
            coverage = report["field_coverage"][field]
            complete = report["complete_fields"][field]
            print(f"  {field:20s}: {coverage:5.1f}% ({complete}/{total} complete)")

    print("\n--- Validation Summary ---")
    print(f"  Valid publications:       {report['validation_summary']['valid']}")
    print(f"  Publications w/ warnings: {report['validation_summary']['warnings']}")
    print(f"  Publications w/ errors:   {report['validation_summary']['errors']}")

    print("\n" + "=" * 60)


def print_results(publications):
    """Print the results in a readable format"""
    print(f"\nFound {len(publications)} publications:\n")
    for i, pub in enumerate(publications, 1):
        print(f"{i}. {pub.get('name', 'Unknown')}")
        print(f"   Author: {pub.get('author', 'Unknown')}")
        print(f"   URL: {pub.get('link', 'N/A')}")
        if pub.get("icon"):
            print(f"   Icon: {pub.get('icon')}")
        print(f"   Paid: {'Yes' if pub.get('is_paid') else 'No'}")
        print()
