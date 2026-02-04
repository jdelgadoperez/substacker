#!/usr/bin/env python3
"""
Substack Reads Scraper - Main Entry Point

Extract and analyze your Substack subscriptions with powerful CLI options.
"""

import argparse

# Import all modules
from modules.config import Config
from modules.cache import clear_cache
from modules.scraper import scrape_substack_reads, extract_rss_url
from modules.ai_labeling import categorize_with_claude
from modules.labeling import filter_labels
from modules.exports import save_to_json, save_to_csv, save_to_opml
from modules.reports import generate_data_quality_report, print_data_quality_report, print_results
from modules.logger import setup_logging, get_logger

logger = get_logger(__name__)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Substack Reads Scraper - Extract and analyze your Substack subscriptions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic usage
  python substack_reads.py

  # Custom URL with verbose output
  python substack_reads.py --url https://substack.com/@user/reads --detailed

  # Disable caching and use sequential downloads
  python substack_reads.py --no-cache --no-parallel

  # Extract metadata with custom workers and timeout
  python substack_reads.py --metadata --workers 10 --timeout 15

  # Filter labels to only keep tech-related ones
  python substack_reads.py --include-labels tech,business,startups

  # Exclude certain labels
  python substack_reads.py --exclude-labels writing,culture

  # Custom output folders
  python substack_reads.py --images-folder ./icons --exports-folder ./data

  # Conservative mode (slow, safe for rate limiting)
  python substack_reads.py --workers 2 --delay 2.0 --no-parallel

  # Include RSS feed URLs in exports
  python substack_reads.py --rss --detailed

  # Export OPML file for feed readers
  python substack_reads.py --opml

  # Export OPML with custom filename
  python substack_reads.py --opml --opml-file my_feeds.opml

  # Full export with RSS and OPML
  python substack_reads.py --rss --opml --metadata --detailed
        '''
    )

    # Input/Output
    parser.add_argument('--url', type=str, default=Config.get_substack_url(),
                        help='Substack reads URL to scrape (default: from .env SUBSTACK_USER)')
    parser.add_argument('--images-folder', type=str, default=None,
                        help='Folder to save downloaded images (default: ~/projects/sandbox/exports/images)')
    parser.add_argument('--exports-folder', type=str, default=None,
                        help='Folder to save exported data (default: ~/projects/sandbox/exports)')

    # Features
    parser.add_argument('--no-images', action='store_true',
                        help='Skip downloading publication icons')
    parser.add_argument('--metadata', action='store_true',
                        help='Extract rich metadata (descriptions, subscriber counts)')
    parser.add_argument('--no-validate', action='store_true',
                        help='Skip data validation')
    parser.add_argument('--no-content-analysis', action='store_true',
                        help='Skip content analysis for labeling')

    # RSS/OPML options
    parser.add_argument('--rss', action='store_true',
                        help='Include RSS feed URLs in JSON/CSV exports')
    parser.add_argument('--opml', action='store_true',
                        help='Export subscriptions as OPML file for feed readers')
    parser.add_argument('--opml-file', type=str, default='substack_feeds.opml',
                        help='Custom OPML filename (default: substack_feeds.opml)')

    # Performance
    parser.add_argument('--no-parallel', action='store_true',
                        help='Disable parallel image downloads')
    parser.add_argument('--workers', type=int, default=5,
                        help='Number of concurrent download threads (default: 5)')
    parser.add_argument('--no-cache', action='store_true',
                        help='Disable content analysis caching')
    parser.add_argument('--no-skip-labeled', action='store_true',
                        help='Always analyze content even if already labeled')

    # Network settings
    parser.add_argument('--timeout', type=int, default=10,
                        help='Request timeout in seconds (default: 10)')
    parser.add_argument('--retries', type=int, default=2,
                        help='Number of retry attempts (default: 2)')
    parser.add_argument('--delay', type=float, default=1.0,
                        help='Rate limit delay between requests in seconds (default: 1.0)')

    # Label filtering
    parser.add_argument('--include-labels', type=str,
                        help='Comma-separated list of labels to include (whitelist)')
    parser.add_argument('--exclude-labels', type=str,
                        help='Comma-separated list of labels to exclude (blacklist)')

    # Output control
    parser.add_argument('--detailed', '-d', action='store_true',
                        help='Show detailed output with full publication list')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Minimal output (errors only)')
    parser.add_argument('--no-report', action='store_true',
                        help='Skip data quality report')

    # Cache management
    parser.add_argument('--clear-cache', action='store_true',
                        help='Clear content analysis cache and exit')
    parser.add_argument('--cache-expiry', type=int, default=7,
                        help='Cache expiry in days (default: 7)')

    # Logging control
    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Logging level (default: INFO)')
    parser.add_argument('--log-file', type=str,
                        help='Write logs to file (in addition to console)')

    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()

    # Setup logging first
    setup_logging(
        level=args.log_level,
        log_file=args.log_file,
        quiet=args.quiet
    )

    # Handle cache clearing
    if args.clear_cache:
        clear_cache()
        return 0

    # Update global config from args
    Config.timeout = args.timeout
    Config.max_retries = args.retries
    Config.rate_limit_delay = args.delay
    Config.max_workers = args.workers
    Config.parallel_downloads = not args.no_parallel
    Config.use_cache = not args.no_cache
    Config.skip_if_labeled = not args.no_skip_labeled
    Config.download_images = not args.no_images
    Config.extract_metadata = args.metadata
    Config.validate_data = not args.no_validate
    Config.analyze_content = not args.no_content_analysis
    # RSS/OPML settings
    Config.include_rss = args.rss or args.opml  # Enable RSS if --rss or --opml
    Config.export_opml = args.opml
    Config.opml_filename = args.opml_file
    # Only override config if user provided custom paths
    if args.images_folder:
        Config.images_folder = args.images_folder
    if args.exports_folder:
        Config.exports_folder = args.exports_folder

    # Parse label filters
    if args.include_labels:
        Config.include_labels = [l.strip() for l in args.include_labels.split(',')]
    if args.exclude_labels:
        Config.exclude_labels = [l.strip() for l in args.exclude_labels.split(',')]

    # Print configuration
    if not args.quiet:
        logger.info("="*60)
        logger.info("SUBSTACK READS SCRAPER - Enhanced Edition")
        logger.info("="*60)
        logger.info(f"Configuration:")
        logger.info(f"  URL: {args.url}")
        logger.info(f"  Parallel downloads: {Config.parallel_downloads} (workers: {Config.max_workers})")
        logger.info(f"  Content caching: {Config.use_cache}")
        logger.info(f"  Timeout: {Config.timeout}s, Retries: {Config.max_retries}, Delay: {Config.rate_limit_delay}s")
        if Config.include_labels:
            logger.info(f"  Include labels: {Config.include_labels}")
        if Config.exclude_labels:
            logger.info(f"  Exclude labels: {Config.exclude_labels}")
        if Config.include_rss:
            logger.info(f"  RSS URLs: enabled")
        if Config.export_opml:
            logger.info(f"  OPML export: {Config.opml_filename}")

    # Run scraper
    publications = scrape_substack_reads(
        args.url,
        download_images=Config.download_images,
        images_folder=Config.images_folder,
        extract_rich_metadata=Config.extract_metadata,
        validate_data=Config.validate_data,
        parallel_downloads=Config.parallel_downloads,
        max_workers=Config.max_workers
    )

    if not publications:
        logger.error("No publications found or error occurred during scraping.")
        return 1

    # Categorize publications with AI
    if not args.quiet:
        logger.info("Categorizing publications with AI...")
    publications = categorize_with_claude(
        publications,
        skip_if_labeled=Config.skip_if_labeled,
    )

    # Apply label filtering
    if Config.include_labels or Config.exclude_labels:
        if not args.quiet:
            logger.info("Applying label filters...")
        publications = filter_labels(
            publications,
            include_labels=Config.include_labels,
            exclude_labels=Config.exclude_labels
        )

    # Add RSS URLs if requested
    if Config.include_rss:
        if not args.quiet:
            logger.info("Extracting RSS feed URLs...")
        for pub in publications:
            if pub.get("link"):
                pub["rss_url"] = extract_rss_url(pub["link"])

    # Show detailed results if requested
    if args.detailed:
        print_results(publications)

    # Generate quality report unless disabled
    if not args.no_report and not args.quiet:
        report = generate_data_quality_report(publications)
        print_data_quality_report(report)

    # Save data
    if not args.quiet:
        logger.info("Saving data...")
    save_to_json(publications, f"{Config.exports_folder}/substack_reads.json")
    save_to_csv(publications, f"{Config.exports_folder}/substack_reads.csv")

    # Export OPML if requested
    if Config.export_opml:
        opml_path = f"{Config.exports_folder}/{Config.opml_filename}"
        save_to_opml(publications, opml_path)

    # Summary
    if not args.quiet:
        logger.info("="*60)
        logger.info("SUMMARY")
        logger.info("="*60)
        logger.info(f"Successfully scraped {len(publications)} publications")
        logger.info(f"Images: {Config.images_folder}/")
        logger.info(f"Data: {Config.exports_folder}/")

    return 0


if __name__ == "__main__":
    exit(main())
