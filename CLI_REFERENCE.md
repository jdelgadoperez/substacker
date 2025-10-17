# Command-Line Interface Reference

Complete reference for the Substack Reads Scraper CLI.

## Quick Start

```bash
# Basic usage (uses defaults from definitions.py)
python substack_reads.py

# Get help
python substack_reads.py --help
```

## Command-Line Arguments

### Input/Output

| Flag | Default | Description |
|------|---------|-------------|
| `--url URL` | From `definitions.py` | Substack reads URL to scrape |
| `--images-folder PATH` | `images` | Folder to save downloaded images |
| `--exports-folder PATH` | `exports` | Folder to save exported data |

### Features

| Flag | Default | Description |
|------|---------|-------------|
| `--no-images` | Images enabled | Skip downloading publication icons |
| `--metadata` | Disabled | Extract rich metadata (descriptions, subscriber counts) |
| `--no-validate` | Validation enabled | Skip data validation |
| `--no-content-analysis` | Analysis enabled | Skip content analysis for labeling |

### Performance

| Flag | Default | Description |
|------|---------|-------------|
| `--no-parallel` | Parallel enabled | Disable parallel image downloads |
| `--workers N` | `5` | Number of concurrent download threads |
| `--no-cache` | Cache enabled | Disable content analysis caching |
| `--no-skip-labeled` | Skip enabled | Always analyze content even if already labeled |

### Network Settings

| Flag | Default | Description |
|------|---------|-------------|
| `--timeout N` | `10` | Request timeout in seconds |
| `--retries N` | `2` | Number of retry attempts |
| `--delay F` | `1.0` | Rate limit delay between requests in seconds |

### Label Filtering

| Flag | Default | Description |
|------|---------|-------------|
| `--include-labels LIST` | None | Comma-separated list of labels to include (whitelist) |
| `--exclude-labels LIST` | None | Comma-separated list of labels to exclude (blacklist) |

### Output Control

| Flag | Default | Description |
|------|---------|-------------|
| `--detailed`, `-d` | Disabled | Show detailed output with full publication list |
| `--quiet`, `-q` | Disabled | Minimal output (errors only) |
| `--no-report` | Report enabled | Skip data quality report |

### Cache Management

| Flag | Default | Description |
|------|---------|-------------|
| `--clear-cache` | N/A | Clear content analysis cache and exit |
| `--cache-expiry N` | `7` | Cache expiry in days |

## Usage Examples

### Basic Usage

```bash
# Default settings
python substack_reads.py

# Custom URL
python substack_reads.py --url https://substack.com/@username/reads
```

### Performance Tuning

```bash
# Maximum speed (10 workers, no delays)
python substack_reads.py --workers 10 --delay 0.5

# Conservative mode (safe for rate limiting)
python substack_reads.py --workers 2 --delay 2.0 --no-parallel

# Disable all caching for fresh data
python substack_reads.py --no-cache --no-skip-labeled
```

### Feature Control

```bash
# Full metadata extraction
python substack_reads.py --metadata

# Skip images, only get data
python substack_reads.py --no-images

# Quick scrape without content analysis
python substack_reads.py --no-content-analysis
```

### Label Filtering

```bash
# Only keep tech-related labels
python substack_reads.py --include-labels tech,software,ai,startups

# Exclude uninteresting labels
python substack_reads.py --exclude-labels free,unsubscribed,following

# Both include and exclude (include applied first)
python substack_reads.py --include-labels tech,business --exclude-labels free
```

### Output Customization

```bash
# Detailed output
python substack_reads.py --detailed

# Quiet mode (only errors)
python substack_reads.py --quiet

# Skip quality report
python substack_reads.py --no-report

# Custom output folders
python substack_reads.py --images-folder ./icons --exports-folder ./data
```

### Network Configuration

```bash
# Increase timeout for slow connections
python substack_reads.py --timeout 30

# More aggressive retries
python substack_reads.py --retries 5

# Slower rate limiting to be respectful
python substack_reads.py --delay 2.5
```

### Cache Management

```bash
# Clear cache
python substack_reads.py --clear-cache

# Set cache expiry to 14 days
python substack_reads.py --cache-expiry 14

# Disable cache
python substack_reads.py --no-cache
```

## Common Workflows

### First-Time Setup

```bash
# Full extraction with metadata
python substack_reads.py --metadata --detailed
```

### Daily Updates

```bash
# Quick incremental update (uses cache, skips labeled)
python substack_reads.py
```

### Clean Re-scrape

```bash
# Clear cache and re-fetch everything
python substack_reads.py --clear-cache
python substack_reads.py --no-cache --no-skip-labeled
```

### Fast Data-Only Scrape

```bash
# No images, no content analysis, just basic data
python substack_reads.py --no-images --no-content-analysis --quiet
```

### Production Mode

```bash
# Reliable settings for automation
python substack_reads.py \
    --workers 3 \
    --timeout 15 \
    --retries 3 \
    --delay 1.5 \
    --no-report \
    --quiet
```

### Development/Testing

```bash
# Sequential, verbose, no cache
python substack_reads.py \
    --no-parallel \
    --no-cache \
    --detailed \
    --workers 1
```

## Configuration Presets

### Speed Preset
```bash
python substack_reads.py \
    --workers 10 \
    --delay 0.5 \
    --timeout 5
```

### Safe Preset
```bash
python substack_reads.py \
    --workers 2 \
    --delay 2.0 \
    --timeout 30 \
    --retries 5
```

### Minimal Preset
```bash
python substack_reads.py \
    --no-images \
    --no-content-analysis \
    --no-report \
    --quiet
```

### Full Analysis Preset
```bash
python substack_reads.py \
    --metadata \
    --detailed \
    --workers 5
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Error (no publications found or scraping failed) |

## Environment Variables

Currently, all configuration is via CLI arguments. Environment variables are not supported but could be added in future versions.

## Tips & Tricks

### 1. Speed vs. Reliability Trade-off

**Fast**:
```bash
--workers 15 --delay 0.3 --timeout 5 --retries 1
```

**Reliable**:
```bash
--workers 3 --delay 2.0 --timeout 30 --retries 5
```

### 2. Debugging

```bash
# Verbose output with no parallelism
python substack_reads.py --detailed --no-parallel --workers 1
```

### 3. Selective Re-scraping

```bash
# Re-analyze only unlabeled publications
python substack_reads.py --no-skip-labeled
```

### 4. Label Management

```bash
# See what labels exist (use --detailed)
python substack_reads.py --detailed | grep "Labels:"

# Filter to specific categories
python substack_reads.py --include-labels tech,business,science
```

### 5. Monitoring Cache Size

```bash
# Check cache size
du -sh .cache/

# See number of cached files
ls .cache/ | wc -l

# Find old cache files (>7 days)
find .cache -name "*.pkl" -mtime +7
```

### 6. Automation Scripts

**Bash script for daily updates**:
```bash
#!/bin/bash
# daily_update.sh
cd /path/to/scraper
python substack_reads.py --quiet
if [ $? -eq 0 ]; then
    echo "✓ Scrape completed successfully"
    # Optional: commit to git, upload to cloud, etc.
fi
```

**Cron job** (daily at 2 AM):
```cron
0 2 * * * cd /path/to/scraper && python substack_reads.py --quiet >> scraper.log 2>&1
```

## Troubleshooting

### Slow Downloads

```bash
# Increase workers
python substack_reads.py --workers 10

# Ensure parallel is enabled
python substack_reads.py --no-no-parallel  # Double negative = enabled
```

### Rate Limiting Issues

```bash
# Slow down requests
python substack_reads.py --delay 3.0 --workers 2

# Use conservative settings
python substack_reads.py --workers 1 --delay 5.0
```

### Timeout Errors

```bash
# Increase timeout and retries
python substack_reads.py --timeout 30 --retries 5
```

### Cache Not Working

```bash
# Verify cache exists
ls -la .cache/

# Clear and rebuild
python substack_reads.py --clear-cache
python substack_reads.py
```

### Out of Memory

```bash
# Reduce workers
python substack_reads.py --workers 2

# Disable parallelism
python substack_reads.py --no-parallel
```

## Integration Examples

### With Git Automation

```bash
#!/bin/bash
# auto_commit.sh
python substack_reads.py --quiet
git add exports/ images/
git commit -m "Auto-update: $(date '+%Y-%m-%d')"
git push
```

### With Data Analysis

```bash
# Export to custom location for analysis
python substack_reads.py --exports-folder ./analysis/data

# Then use in your analysis script
```

## Future Enhancements

Potential CLI improvements:
- [ ] Config file support (`.substackrc`)
- [ ] Environment variable support
- [ ] Interactive mode
- [ ] JSON output format option
- [ ] Webhook notifications
- [ ] Progress bar option
- [ ] Dry-run mode
- [ ] Filter by subscription status
- [ ] Sort options for output
