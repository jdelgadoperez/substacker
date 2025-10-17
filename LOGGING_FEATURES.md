# Logging & Monitoring Features

## Overview

The Substack scraper now features a comprehensive logging and monitoring system that provides:
- **Structured logging** with configurable levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Progress bars** for long-running operations
- **Colored console output** for better readability
- **File logging** support for persistent logs
- **Quiet mode** for minimal output

## New Module: `modules/logger.py`

### Features

1. **Colored Console Output**
   - Green for INFO messages
   - Yellow for WARNING messages
   - Red for ERROR messages
   - Cyan for DEBUG messages
   - Magenta for CRITICAL messages

2. **Progress Bar**
   - Visual progress tracking for batch operations
   - Shows current item count, percentage, and status
   - Automatically completes when done

3. **Flexible Configuration**
   - Console logging with color support
   - Optional file logging
   - Quiet mode (errors only)

### Usage

```python
from modules.logger import setup_logging, get_logger, ProgressBar

# Setup logging
setup_logging(level='INFO', log_file='scraper.log', quiet=False)

# Get a logger for your module
logger = get_logger(__name__)

# Use logging
logger.info("Starting scrape...")
logger.warning("Timeout detected, retrying...")
logger.error("Failed to fetch URL")
logger.debug("Cache hit for metadata")

# Use progress bar
progress = ProgressBar(100, "Processing items")
for i in range(100):
    # Do work...
    progress.update(1, f"Item {i}")
```

## CLI Arguments

### New Logging Arguments

```bash
--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
    Set the logging level (default: INFO)

--log-file PATH
    Write logs to a file in addition to console output
```

### Examples

```bash
# Debug mode with file logging
python substack_reads.py --log-level DEBUG --log-file scraper.log

# Quiet mode (errors only)
python substack_reads.py --quiet

# Info level (default)
python substack_reads.py

# Warning level and above
python substack_reads.py --log-level WARNING
```

## Logging Hierarchy

### Module-Level Logging

Each module now has its own logger:

- `modules.scraper` - Core scraping operations
- `modules.metadata` - Metadata extraction
- `modules.labeling` - Auto-labeling
- `modules.downloads` - Image downloads
- `modules.cache` - Cache operations
- `modules.validation` - Data validation
- `__main__` - Main script orchestration

### Log Levels by Operation

| Operation | Level | Example |
|-----------|-------|---------|
| Configuration | INFO | "Parallel downloads: True (workers: 5)" |
| Scraping start | INFO | "Found 50 potential publications to scrape" |
| Publication extraction | DEBUG | "Extracting metadata for Newsletter..." |
| Validation warnings | WARNING | "Skipping invalid publication: XYZ" |
| Validation errors | DEBUG | "Validation error: Missing URL" |
| Network errors | ERROR | "Error fetching the page: Timeout" |
| Cache operations | DEBUG | "Using cached content analysis" |
| Image downloads | INFO | "Images: 10 cached, 5 newly downloaded" |
| Summary | INFO | "Successfully scraped 50 publications" |

## Progress Bars

The scraper now shows progress bars for:

1. **Publication Extraction**
   - Shows current publication being processed
   - Updates with publication name or "Skipped" status

2. **Image Downloads** (sequential mode)
   - Shows download progress with "cached" or "downloaded" status
   - Displays current publication name

3. **Auto-Labeling**
   - Shows labeling progress for each publication
   - Indicates skipped publications (already labeled)

### Progress Bar Example

```
Extracting publications |████████████████████████░░░░░░| 45/50 (90.0%) Tech Newsletter...
```

## Quiet Mode

Use `--quiet` or `-q` for minimal output:

```bash
python substack_reads.py --quiet
```

In quiet mode:
- Only ERROR and CRITICAL messages shown
- No progress bars
- No configuration output
- No summary statistics
- Useful for cron jobs or scripting

## File Logging

Enable file logging to keep persistent logs:

```bash
python substack_reads.py --log-file scraper.log
```

File logs include:
- Timestamps for all events
- Module names
- Full DEBUG-level output (regardless of console level)
- Useful for debugging and auditing

### Log File Format

```
2025-10-17 12:34:56 - modules.scraper - INFO - Found 50 potential publications to scrape
2025-10-17 12:34:57 - modules.scraper - DEBUG - Extracting metadata for Tech Newsletter...
2025-10-17 12:34:58 - modules.metadata - WARNING - Timeout after 2 attempts for https://example.com
2025-10-17 12:35:00 - modules.scraper - INFO - Successfully scraped 50 publications
```

## Migration from Print Statements

All `print()` statements have been replaced with appropriate logging calls:

| Old Code | New Code | Level |
|----------|----------|-------|
| `print(f"Found {n} publications")` | `logger.info(f"Found {n} publications")` | INFO |
| `print(f"Error: {e}")` | `logger.error(f"Error: {e}")` | ERROR |
| `print(f"  Skipping...")` | `logger.debug(f"Skipping...")` | DEBUG |
| `print(f"  Timeout, retrying...")` | `logger.debug(f"Timeout, retrying...")` | DEBUG |

### Exception: Reports Module

The `reports.py` module still uses `print()` for report output because:
- Reports are meant to be displayed to the user
- They're structured tabular output
- They should appear regardless of log level

## Benefits

### 1. Better Debugging
- Use `--log-level DEBUG` to see detailed operation flow
- File logging captures everything for later analysis
- Module-level loggers make it easy to identify source of messages

### 2. Production Ready
- Use `--quiet` for cron jobs
- Use `--log-level WARNING` to only see issues
- Log files provide audit trail

### 3. Better UX
- Progress bars show real-time status
- Colored output highlights important messages
- Clean, structured logging output

### 4. Maintainability
- Consistent logging format across all modules
- Easy to add new log messages
- Centralized logging configuration

## Common Workflows

### Development

```bash
# Verbose output with file logging
python substack_reads.py --log-level DEBUG --log-file dev.log --detailed
```

### Production

```bash
# Info level with file logging
python substack_reads.py --log-file production.log
```

### Scheduled Jobs

```bash
# Quiet mode, log errors to file
python substack_reads.py --quiet --log-file /var/log/scraper.log
```

### Troubleshooting

```bash
# Debug level to see everything
python substack_reads.py --log-level DEBUG --no-cache
```

## Performance Impact

The logging system has **minimal performance impact**:
- Logging calls are lightweight
- Progress bars update efficiently
- File I/O is buffered
- Debug messages only evaluated if DEBUG level enabled

## Future Enhancements

Potential future features:
- JSON-formatted logging for log aggregation
- Rotating log files
- Remote logging (syslog, cloud logging)
- Performance metrics logging
- Structured logging with context
