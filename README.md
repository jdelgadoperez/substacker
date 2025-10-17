# Substacker

A powerful, production-ready Python scraper for extracting and analyzing your Substack subscriptions with intelligent categorization.

## Features

- ✅ **Comprehensive Data Extraction**: Names, authors, URLs, icons, payment status, metadata
- ✅ **Smart Caching**: Content analysis caching with 7-day expiry (300x speedup)
- ✅ **Parallel Downloads**: 5x faster image downloads with configurable workers
- ✅ **Intelligent Auto-Labeling**:
  - Multi-source analysis (name, author, URL, content, known authors)
  - Weighted scoring system (4-point scale)
  - 40+ keyword categories with expanded vocabulary
  - Known authors database for accurate categorization
  - Fallback strategies for minimal-content publications
- ✅ **Data Validation**: URL validation, duplicate detection, quality reports
- ✅ **Multiple Export Formats**: JSON and CSV exports
- ✅ **Progress Tracking**: Visual progress bars for all operations
- ✅ **Professional Logging**: Colored console output, file logging, quiet mode
- ✅ **Secure Configuration**: Environment variable management for credentials

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Substack cookie
# See ENV_CONFIGURATION.md for detailed instructions
```

### 3. Run the Scraper

```bash
# Basic usage
python substack_reads.py

# With all features
python substack_reads.py --metadata --workers 10 --detailed

# Quiet mode for automation
python substack_reads.py --quiet --log-file scraper.log
```

## Documentation

- **[Environment Configuration](ENV_CONFIGURATION.md)** - Setting up credentials and API tokens
- **[CLI Reference](CLI_REFERENCE.md)** - Complete command-line reference (30+ options)
- **[Logging Features](LOGGING_FEATURES.md)** - Logging levels, progress bars, file logging
- **[Performance Improvements](PERFORMANCE_IMPROVEMENTS.md)** - Parallel downloads, caching, optimization
- **[Data Quality Features](DATA_QUALITY_FEATURES.md)** - Validation, duplicate detection, reports
- **[Refactoring Summary](REFACTORING_SUMMARY.md)** - Modular architecture details

## Common Usage Examples

### Development

```bash
# Full featured with debug logging
python substack_reads.py \\
  --metadata \\
  --workers 10 \\
  --log-level DEBUG \\
  --log-file debug.log \\
  --detailed
```

### Production

```bash
# Fast, cached, with logging
python substack_reads.py \\
  --workers 10 \\
  --log-file production.log
```

### Scheduled Jobs

```bash
# Quiet mode, errors only
python substack_reads.py \\
  --quiet \\
  --log-file /var/log/scraper.log
```

### Conservative (Rate-Limited)

```bash
# Slow, safe, sequential
python substack_reads.py \\
  --workers 2 \\
  --delay 2.0 \\
  --no-parallel
```

## Output

### Files Generated

```
exports/
├── substack_reads.json    # Full data with all fields
└── substack_reads.csv     # Tabular format for spreadsheets

images/
└── [publication icons]    # Downloaded publication icons
```

### JSON Structure

```json
{
  "name": "Tech Newsletter",
  "author": "John Doe",
  "link": "https://technewsletter.substack.com",
  "icon": "/absolute/path/to/icon.jpg",
  "is_paid": false,
  "subscription_status": "Subscribed",
  "description": "Weekly tech insights...",
  "subscriber_info": "10,000 subscribers",
  "labels": ["tech", "free", "subscribed"]
}
```

## Architecture

### Modular Design

```
scrape/substack/
├── substack_reads.py       # Main entry point (222 lines)
├── definitions.py          # Configuration and constants
├── modules/
│   ├── logger.py           # Logging and progress bars
│   ├── config.py           # Global configuration
│   ├── cache.py            # Content caching
│   ├── validation.py       # Data validation
│   ├── metadata.py         # Content extraction
│   ├── labeling.py         # Auto-labeling
│   ├── downloads.py        # Image downloads
│   ├── scraper.py          # Core scraping
│   ├── exports.py          # Data export
│   └── reports.py          # Quality reports
└── [documentation files]
```

### Key Benefits

- **82% reduction** in main script size (1,248 → 222 lines)
- **9 focused modules** averaging ~100 lines each
- **100% backward compatibility**
- **Zero performance impact**
- **Dramatically improved maintainability**

## Configuration

### Environment Variables

Required:
- `SUBSTACK_COOKIE` - Your Substack session cookie

Optional:
- `SUBSTACK_USER` - Your username
- `NOTION_TOKEN` - Notion API token (for exports)
- `DATABASE_ID` - Notion database ID

See [ENV_CONFIGURATION.md](ENV_CONFIGURATION.md) for details.

### CLI Flags

**Features:**
- `--metadata` - Extract rich metadata (descriptions, subscriber counts)
- `--no-images` - Skip image downloads
- `--no-validate` - Skip data validation
- `--no-content-analysis` - Skip content analysis for labeling

**Performance:**
- `--workers N` - Number of parallel workers (default: 5)
- `--no-parallel` - Disable parallel downloads
- `--no-cache` - Disable content caching
- `--timeout N` - Request timeout in seconds
- `--retries N` - Number of retry attempts
- `--delay N` - Rate limit delay in seconds

**Logging:**
- `--log-level LEVEL` - DEBUG, INFO, WARNING, ERROR, CRITICAL
- `--log-file PATH` - Write logs to file
- `--quiet` - Minimal output (errors only)
- `--detailed` - Show full publication list

**Labels:**
- `--include-labels tech,business` - Whitelist labels
- `--exclude-labels free,unsubscribed` - Blacklist labels

See [CLI_REFERENCE.md](CLI_REFERENCE.md) for complete reference.

## Performance

### Benchmarks

| Feature | Baseline | Optimized | Improvement |
|---------|----------|-----------|-------------|
| Image Downloads | 50s | 10s | **5x faster** |
| Content Analysis (cached) | 300s | 1s | **300x faster** |
| Partial Updates | 100% time | 10% time | **90% faster** |

### Optimization Features

1. **Parallel Downloads**: ThreadPoolExecutor with 5 workers (configurable)
2. **Smart Caching**: Pickle-based cache with MD5 keys and 7-day expiry
3. **Skip Logic**: Skip already-labeled publications and cached images
4. **Rate Limiting**: Configurable delays to avoid overwhelming servers

See [PERFORMANCE_IMPROVEMENTS.md](PERFORMANCE_IMPROVEMENTS.md) for details.

## Data Quality

### Validation Features

- URL validation and normalization
- Required field checking
- Suspicious data detection
- Duplicate detection (fuzzy matching)

### Quality Reports

```
DATA QUALITY REPORT
============================================================

Total Publications: 50

--- Payment Breakdown ---
  Paid:     15 (30.0%)
  Free:     35 (70.0%)

--- Field Coverage ---
  name                : 100.0% (50/50 complete)
  link                : 100.0% (50/50 complete)
  author              :  98.0% (49/50 complete)
  icon                :  96.0% (48/50 complete)
  description         :  80.0% (40/50 complete)
```

See [DATA_QUALITY_FEATURES.md](DATA_QUALITY_FEATURES.md) for details.

## Requirements

- Python 3.7+
- requests >= 2.31.0
- beautifulsoup4 >= 4.12.0
- python-dotenv >= 1.0.0

## Security

- **Environment Variables**: Sensitive credentials stored in `.env` (not committed)
- **Gitignore**: `.env` file automatically excluded from version control
- **Cookie Rotation**: Easy to update cookies when they expire

## Troubleshooting

### Authentication Errors

**Problem**: Scraper can't access your subscriptions

**Solution**: Update your Substack cookie in `.env` (see ENV_CONFIGURATION.md)

### Missing Dependencies

**Problem**: `ModuleNotFoundError`

**Solution**: `pip install -r requirements.txt`

### Slow Performance

**Problem**: Scraping takes too long

**Solutions**:
- Increase workers: `--workers 10`
- Enable caching: Remove `--no-cache`
- Use parallel downloads: Remove `--no-parallel`

### Rate Limiting

**Problem**: Getting 429 errors

**Solutions**:
- Reduce workers: `--workers 2`
- Add delay: `--delay 2.0`
- Use sequential downloads: `--no-parallel`

## Contributing

The codebase is modular and well-documented. To add features:

1. Choose the appropriate module or create a new one
2. Follow existing patterns (logging, error handling)
3. Update relevant documentation
4. Test with `--log-level DEBUG`

## Auto-Labeling System

Substacker uses a sophisticated multi-layered labeling system:

### Categorization Features

1. **Multi-Source Analysis**:
   - Publication name (3 points)
   - Author bio from known authors database (4 points)
   - URL structure (2 points)
   - Page content (1.5 points)
   - Author field (1 point)

2. **40+ Categories**: tech, ai, crypto, startups, business, finance, marketing, news, politics, culture, law, health, science, writing, music, and more

3. **Smart Matching**:
   - Word boundary detection (prevents false positives)
   - Multi-word phrase support
   - Case-insensitive matching

4. **Known Authors Database**: Pre-configured information for notable authors (easily extensible in `definitions.py`)

5. **Fallback Strategies**: Contextual inference for publications with minimal metadata

### Example Results

```json
{
  "name": "Davey Havok",
  "author": "by Davey Havok",
  "labels": ["music", "music-focused", "paid"]
},
{
  "name": "Legally Trans",
  "author": "by Chase Strangio",
  "labels": ["culture", "culture-focused", "law", "law-focused", "paid", "politics"]
}
```

## License

MIT License - see LICENSE file for details

## Version History

- **v2.0.0** - Modular refactoring, logging system, environment configuration
- **v1.5.0** - Performance improvements, caching, parallel downloads
- **v1.0.0** - Initial release with basic scraping

---

**Built with ❤️ for Substack enthusiasts**
