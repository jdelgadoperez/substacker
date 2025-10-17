# Substack Scraper Modules

This directory contains the modular components of the Substack Reads Scraper.

## Module Structure

```
modules/
├── __init__.py         # Package initialization
├── config.py           # Configuration class and constants
├── cache.py            # Content analysis caching
├── validation.py       # URL and data validation
├── metadata.py         # Content extraction and analysis
├── labeling.py         # Auto-labeling and label filtering
├── downloads.py        # Image downloads (parallel & sequential)
├── scraper.py          # Core scraping logic
├── exports.py          # CSV/JSON export functions
└── reports.py          # Data quality reporting
```

## Module Descriptions

### config.py
- **Purpose**: Central configuration management
- **Key Components**:
  - `Config` class with all settings
  - Cache directory and expiry constants
- **Usage**: Import and modify Config attributes to change behavior

### cache.py
- **Purpose**: Manage content analysis cache
- **Key Functions**:
  - `get_cached_metadata(url)` - Retrieve cached data
  - `save_cached_metadata(url, metadata)` - Save to cache
  - `clear_cache()` - Clear all cached data
- **Cache Storage**: `.cache/` directory with pickle files

### validation.py
- **Purpose**: Validate URLs and publication data
- **Key Functions**:
  - `validate_url(url)` - Check URL format and structure
  - `validate_publication_data(pub)` - Validate publication fields
  - `find_duplicates(publications)` - Detect similar publications
  - `calculate_similarity(str1, str2)` - Fuzzy string matching

### metadata.py
- **Purpose**: Extract metadata from publication pages
- **Key Functions**:
  - `extract_metadata(url)` - Fetch and parse publication metadata
  - `analyze_publication_content(url)` - Get content text for analysis
- **Extracted Data**: Description, subscriber info, about text, content text

### labeling.py
- **Purpose**: Auto-label publications and filter labels
- **Key Functions**:
  - `auto_label_publications(publications)` - Apply labels based on content
  - `filter_labels(publications)` - Include/exclude specific labels
- **Label Types**: Payment status, subscription status, topic categories

### downloads.py
- **Purpose**: Download publication icons
- **Key Functions**:
  - `download_image(url, folder, filename)` - Single image download
  - `download_images_parallel(tasks, workers)` - Parallel downloads
  - `sanitize_filename(filename)` - Clean filenames for filesystem
- **Features**: Caching, parallel execution, error handling

### scraper.py
- **Purpose**: Core scraping logic for Substack reads page
- **Key Functions**:
  - `scrape_substack_reads(url, ...)` - Main scraping function
- **Process**: Parse HTML → Extract data → Validate → Download images
- **Returns**: List of publication dictionaries

### exports.py
- **Purpose**: Export data to various formats
- **Key Functions**:
  - `save_to_json(data, filename)` - Export to JSON
  - `save_to_csv(data, filename)` - Export to CSV
- **Features**: Auto-create directories, dynamic field detection

### reports.py
- **Purpose**: Generate and display data quality reports
- **Key Functions**:
  - `generate_data_quality_report(publications)` - Create report
  - `print_data_quality_report(report)` - Display formatted report
  - `print_results(publications)` - Show publication list
- **Metrics**: Field coverage, validation summary, payment breakdown

## Dependencies Between Modules

```
config.py (base)
    ↓
cache.py → metadata.py → labeling.py
    ↓            ↓            ↓
validation.py ←  ↓            ↓
    ↓            ↓            ↓
downloads.py ←   ↓            ↓
    ↓            ↓            ↓
scraper.py ← ←  ← ← ← ← ← ← ←
    ↓
exports.py, reports.py
```

## Using the Modules

### In the Main Script
```python
from modules.config import Config
from modules.scraper import scrape_substack_reads
from modules.labeling import auto_label_publications
from modules.exports import save_to_json

# Configure
Config.max_workers = 10

# Scrape
publications = scrape_substack_reads(url)

# Label
publications = auto_label_publications(publications)

# Export
save_to_json(publications, "output.json")
```

### In Custom Scripts
```python
# Use individual modules as needed
from modules.validation import validate_url
from modules.cache import get_cached_metadata

# Validate a URL
is_valid, cleaned_url, error = validate_url("example.com")

# Check cache
metadata = get_cached_metadata("https://example.substack.com")
```

## Testing Modules Individually

Each module can be tested independently:

```python
# Test cache module
from modules.cache import save_cached_metadata, get_cached_metadata

test_data = {'description': 'Test publication', 'content_text': 'lorem ipsum'}
save_cached_metadata("https://test.com", test_data)
cached = get_cached_metadata("https://test.com")
assert cached == test_data
```

## Module Benefits

1. **Maintainability**: Each module has a single, clear purpose
2. **Testability**: Modules can be tested independently
3. **Reusability**: Modules can be used in other scripts
4. **Readability**: Main script is now ~220 lines vs ~1200 lines
5. **Extensibility**: Easy to add new modules without touching existing code

## File Sizes

- **Original**: `substack_reads.py` - 1,248 lines
- **New Main**: `substack_reads.py` - 222 lines (82% reduction!)
- **Modules**: Each 50-150 lines (focused and manageable)

## Future Enhancements

Potential new modules:
- `notifications.py` - Email/webhook notifications
- `storage.py` - Database storage (SQLite, PostgreSQL)
- `analytics.py` - Data analysis and statistics
- `api.py` - REST API interface
- `scheduler.py` - Cron-like scheduling
