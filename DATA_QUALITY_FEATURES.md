# Data Quality Features

This document describes the data quality features built into Substacker.

## Features

### 1. URL Validation
- **Function**: `validate_url(url)`
- Validates URL format and structure
- Automatically adds `https://` if missing
- Checks for valid scheme, domain, and components
- Returns: `(is_valid, cleaned_url, error_message)`

### 2. Publication Data Validation
- **Function**: `validate_publication_data(pub, strict=False)`
- Validates required fields (name, link)
- Checks optional fields (author, payment status, subscription status)
- Validates icon file paths (checks if absolute and exists)
- Detects suspicious data (very long names, short names)
- Returns: `(is_valid, errors, warnings)`
- **Strict mode**: Treats warnings as errors

### 3. Smart Image Caching
- **Function**: `download_image(url, folder_path, filename, skip_if_exists=True)`
- **Key Feature**: Prevents duplicate image downloads
- Filenames based on publication name (not index), ensuring consistency across runs
- Checks if image already exists before downloading
- Validates existing images (size > 0)
- Re-downloads corrupted/empty files
- Preserves original image extension from URL

**Benefits**:
- No duplicate images on repeated runs
- Faster scraping (skips already-downloaded images)
- Consistent filenames: `Publication_Name.jpg` instead of `01_Publication_Name.jpg`

### 4. Enhanced Metadata Extraction
- **Function**: `extract_metadata(url, max_retries=2)`
- Extracts rich metadata from publication home pages:
  - `description`: Meta description from page
  - `subscriber_info`: Subscriber/reader counts
  - `about_text`: Content from "About" sections
  - `content_text`: Combined text for keyword analysis
- Includes retry logic for timeout handling
- Respects rate limits with delays

### 5. Data Quality Report
- **Function**: `generate_data_quality_report(publications)`
- Generates comprehensive quality metrics:
  - Total publication count
  - Payment breakdown (paid vs. free)
  - Subscription status distribution
  - Field coverage percentages
  - Validation summary (valid, warnings, errors)

- **Function**: `print_data_quality_report(report)`
- Formats and displays the quality report in a readable format
- Shows payment breakdown with percentages
- Lists subscription statuses (subscribed, following, etc.)
- Key field coverage summary

### 6. Enhanced Scraping Function
**Updated**: `scrape_substack_reads()` now includes:
- `extract_rich_metadata`: Optional deep metadata extraction
- `validate_data`: Automatic validation during scraping
- Progress indicators (e.g., `[3/50]`)
- Image caching indicators (✓ cached, ↓ downloaded)
- Skipped publication tracking
- Better error messages with symbols (✓, ✗, ⚠)
- Consistent filename generation based on publication name

### 7. Improved Export Functions
- **CSV Export**:
  - Auto-creates `exports/` directory
  - Dynamic field detection (includes all fields found)
  - Preferred field ordering
  - Converts lists to comma-separated strings

- **JSON Export**:
  - Auto-creates `exports/` directory
  - Pretty-printed with indentation

## Usage Examples

### Basic Usage (with validation)
```python
publications = scrape_substack_reads(
    SUBSTACK_URL,
    download_images=True,
    validate_data=True  # Validates during scraping
)
```

### With Rich Metadata Extraction
```python
publications = scrape_substack_reads(
    SUBSTACK_URL,
    download_images=True,
    extract_rich_metadata=True,  # Fetches descriptions, subscriber counts
    validate_data=True
)
```

### Generate Quality Report
```python
report = generate_data_quality_report(publications)
print_data_quality_report(report)
```

### Manual Validation
```python
is_valid, errors, warnings = validate_publication_data(pub)
if not is_valid:
    print(f"Errors: {errors}")
if warnings:
    print(f"Warnings: {warnings}")
```

### Image Caching
```python
# First run: Downloads all images
local_path = download_image(icon_url, "images", "Newsletter_Name.jpg")

# Second run: Reuses existing images (much faster!)
local_path = download_image(icon_url, "images", "Newsletter_Name.jpg")  # Skips download
```

### Validate Individual URL
```python
is_valid, cleaned_url, error = validate_url("example.com/newsletter")
# Returns: (True, "https://example.com/newsletter", None)
```

## Command Line Flags

### Standard Mode (default)
```bash
python substack_reads.py
```
- Scrapes with validation
- Shows data quality report
- Saves to JSON and CSV

### Detailed Mode
```bash
python substack_reads.py --detailed
# or
python substack_reads.py -d
```
- Shows full publication list
- Includes quality report
- More verbose output

### With Metadata Extraction
```bash
python substack_reads.py --detailed --metadata
```
- Enables rich metadata extraction
- Fetches descriptions, subscriber counts, about text
- Takes longer but provides richer data

## Output Example

### First Run (Downloads images)
```
============================================================
SUBSTACK READS SCRAPER - Enhanced Edition
============================================================

Scraping Substack reads page...
Found 45 potential publications to scrape
  [1/45] ↓ Downloaded image for Tech Weekly
  [2/45] ↓ Downloaded image for The Daily Brief
  [3/45] ⚠ Warnings for Newsletter Name:
    - Missing author information
  [3/45] ↓ Downloaded image for Newsletter Name

✓ Successfully scraped 45 publications
✗ Skipped 0 invalid publications

============================================================
DATA QUALITY REPORT
============================================================

Total Publications: 45

--- Payment Breakdown ---
  Paid:     12 (26.7%)
  Free:     33 (73.3%)

--- Subscription Status ---
  Subscribed          :  28 (62.2%)
  Following           :  15 (33.3%)
  Unsubscribed        :   2 (4.4%)

--- Field Coverage ---
  name                : 100.0% (45/45 complete)
  link                : 100.0% (45/45 complete)
  icon                : 100.0% (45/45 complete)
  is_paid             :  97.8% (44/45 complete)
  author              :  88.9% (40/45 complete)
  subscription_status : 100.0% (45/45 complete)
  labels              :  91.1% (41/45 complete)

--- Validation Summary ---
  Valid publications:       45
  Publications w/ warnings:  5
  Publications w/ errors:    0

============================================================
```

### Second Run (Reuses cached images - much faster!)
```
============================================================
SUBSTACK READS SCRAPER - Enhanced Edition
============================================================

Scraping Substack reads page...
Found 45 potential publications to scrape
  [1/45] ✓ Image for Tech Weekly (cached)
  [2/45] ✓ Image for The Daily Brief (cached)
  [3/45] ✓ Image for Newsletter Name (cached)

✓ Successfully scraped 45 publications
✗ Skipped 0 invalid publications
```

## Configuration

All validation thresholds and settings can be adjusted:

```python
# Duplicate detection threshold
duplicates = find_duplicates(publications, similarity_threshold=0.90)  # More strict

# Strict validation mode (warnings become errors)
is_valid, errors, warnings = validate_publication_data(pub, strict=True)

# Metadata extraction with more retries
metadata = extract_metadata(url, max_retries=3)
```

## New Data Fields

When using `extract_rich_metadata=True`, publications will include:
- `description`: Publication description from meta tags
- `subscriber_info`: Subscriber/reader count (e.g., "15K subscribers")
- `about_text`: Text from the publication's About section

## Benefits

1. **Data Integrity**: Catches invalid URLs and missing required fields
2. **No Duplicate Images**: Smart caching prevents duplicate downloads on repeated runs
3. **Faster Reruns**: Cached images mean subsequent runs are much faster
4. **Rich Metadata**: Optional extraction of descriptions and subscriber counts
5. **Quality Visibility**: Comprehensive reporting on data completeness and distribution
6. **Better Exports**: Dynamic field detection ensures no data is lost
7. **Error Prevention**: Validation before saving prevents corrupt data
8. **Consistent Filenames**: Images always have the same name based on publication name
