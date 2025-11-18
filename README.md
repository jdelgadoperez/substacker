# Substacker

A powerful, production-ready Python scraper for extracting and analyzing your Substack subscriptions with intelligent categorization.

## Features

- ✅ **Comprehensive Data Extraction**: Names, authors, URLs, icons, payment status, metadata
- ✅ **Smart Caching**: Content analysis caching with 7-day expiry (300x speedup)
- ✅ **Parallel Downloads**: 5x faster image downloads with configurable workers
- ✅ **Intelligent Auto-Labeling**:
  - Multi-source analysis (name, author, URL, content, author profiles)
  - Weighted scoring system (4-point scale)
  - 40+ keyword categories with expanded vocabulary
  - Automatic author profile fetching from Substack
  - Fallback strategies for minimal-content publications
- ✅ **Data Validation**: URL validation, duplicate detection, quality reports
- ✅ **Multiple Export Formats**: JSON and CSV exports
- ✅ **Progress Tracking**: Visual progress bars for all operations
- ✅ **Professional Logging**: Colored console output, file logging, quiet mode
- ✅ **Secure Configuration**: Environment variable management for credentials

## System Requirements

### Minimum Requirements
- **Python**: 3.9 or higher (tested on 3.9, 3.10, 3.11, 3.12, 3.13)
- **Operating System**: Windows, macOS, or Linux
- **Disk Space**: ~50MB for dependencies + storage for images/exports
- **Internet**: Required for scraping and downloading

### Dependencies
- `requests` (2.31.0+) - HTTP library for web scraping
- `beautifulsoup4` (4.12.0+) - HTML parsing
- `python-dotenv` (1.0.0+) - Environment variable management

All standard library features (JSON, CSV, threading, etc.) are included with Python.

## Installation

### For First-Time Users

**1. Check Python Version**

```bash
python --version
# or
python3 --version
```

If Python is not installed or version is below 3.9, download from [python.org](https://www.python.org/downloads/)

**2. Clone or Download Repository**

```bash
# Option A: Using git
git clone <repository-url>
cd substacker

# Option B: Download ZIP
# Extract the ZIP file and navigate to the folder
cd substacker
```

**3. Create Virtual Environment (Recommended)**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

**4. Install Dependencies**

```bash
pip install -r requirements.txt
```

Expected output:
```
Collecting requests>=2.31.0
Collecting beautifulsoup4>=4.12.0
Collecting python-dotenv>=1.0.0
...
Successfully installed beautifulsoup4-4.12.0 requests-2.31.0 python-dotenv-1.0.0
```

### Quick Install (Advanced Users)

```bash
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

## Quick Start

**New to this?** Check out the [Complete Beginner's Guide](GETTING_STARTED.md) for detailed setup instructions with screenshots.

### 1. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your credentials
# SUBSTACK_USER="@yourusername"
# SUBSTACK_COOKIE="paste_your_cookie_here"
```

**Quick method to get your cookie:**

1. Log into [substack.com](https://substack.com)
2. Press `F12` → Network tab
3. Refresh page, click any request
4. Copy the `Cookie` header value

See the [detailed cookie guide](GETTING_STARTED.md#getting-your-substack-cookie) for step-by-step instructions for Chrome, Firefox, and Safari.

### 2. Run the Scraper

```bash
# Basic usage
python substack_reads.py

# With all features
python substack_reads.py --metadata --workers 10 --detailed

# Quiet mode for automation
python substack_reads.py --quiet --log-file scraper.log
```

## Documentation

- **[Getting Started Guide](GETTING_STARTED.md)** - Complete beginner's guide with cookie setup instructions
- **[Environment Configuration](ENV_CONFIGURATION.md)** - Setting up credentials and environment variables
- **[CLI Reference](CLI_REFERENCE.md)** - Complete command-line reference (30+ options)
- **[Logging Features](LOGGING_FEATURES.md)** - Logging levels, progress bars, file logging
- **[Performance Features](PERFORMANCE_FEATURES.md)** - Parallel downloads, caching, optimization
- **[Data Quality Features](DATA_QUALITY_FEATURES.md)** - Validation, duplicate detection, reports

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
	"labels": ["tech"]
}
```

## Architecture

### Modular Design

```
substacker/
├── substack_reads.py       # Main entry point (240 lines)
├── definitions.py          # DEPRECATED: Backward compatibility shim
├── .llm/
│   └── plans/              # Implementation plans and design docs
├── modules/
│   ├── config.py           # Unified configuration (env, network, features)
│   ├── categories.py       # Keyword categories (40+ categories)
│   ├── logger.py           # Logging and progress bars
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

- **Lightweight main script**: 240 lines (orchestration only)
- **Unified configuration**: All settings in `modules/config.py`
- **Separated domain knowledge**: Categories in dedicated module
- **10 focused modules** averaging ~100 lines each
- **Clear separation of concerns**
- **High reusability and testability**
- **Easy to extend and maintain**

## Configuration

### Environment Variables

Required:

- `SUBSTACK_COOKIE` - Your Substack session cookie
- `SUBSTACK_USER` - Your Substack username

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
- `--exclude-labels writing,culture` - Blacklist labels

See [CLI_REFERENCE.md](CLI_REFERENCE.md) for complete reference.

## Performance

### Benchmarks

| Feature                   | Baseline  | Optimized | Improvement     |
| ------------------------- | --------- | --------- | --------------- |
| Image Downloads           | 50s       | 10s       | **5x faster**   |
| Content Analysis (cached) | 300s      | 1s        | **300x faster** |
| Partial Updates           | 100% time | 10% time  | **90% faster**  |

### Optimization Features

1. **Parallel Downloads**: ThreadPoolExecutor with 5 workers (configurable)
2. **Smart Caching**: Pickle-based cache with MD5 keys and 7-day expiry
3. **Skip Logic**: Skip already-labeled publications and cached images
4. **Rate Limiting**: Configurable delays to avoid overwhelming servers

See [PERFORMANCE_FEATURES.md](PERFORMANCE_FEATURES.md) for details.

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

## Security

- **Environment Variables**: Sensitive credentials stored in `.env` (not committed)
- **Gitignore**: `.env` file automatically excluded from version control
- **Cookie Rotation**: Easy to update cookies when they expire

## Troubleshooting

### Installation Issues

#### Python Version Too Old

**Problem**: `SyntaxError` or features not working

**Solution**:
```bash
# Check your Python version
python --version

# If below 3.9, download from python.org
# Or use Python 3.9+ via pyenv, conda, etc.
```

#### ModuleNotFoundError

**Problem**:
```
ModuleNotFoundError: No module named 'requests'
ModuleNotFoundError: No module named 'bs4'
ModuleNotFoundError: No module named 'dotenv'
```

**Solution**:
```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "requests|beautifulsoup4|python-dotenv"
```

#### Permission Denied

**Problem**: `PermissionError` when installing packages

**Solution**:
```bash
# Option 1: Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Option 2: Install for user only (not recommended)
pip install --user -r requirements.txt
```

#### pip Command Not Found

**Problem**: `bash: pip: command not found`

**Solution**:
```bash
# Try pip3 instead
pip3 install -r requirements.txt

# Or use Python module syntax
python -m pip install -r requirements.txt
python3 -m pip install -r requirements.txt
```

### Runtime Issues

#### Authentication Errors

**Problem**: Scraper can't access your subscriptions

**Solution**:
1. Get a fresh cookie from your browser
2. Update `.env` file with new `SUBSTACK_COOKIE`
3. Make sure you're logged into Substack in your browser
4. See [ENV_CONFIGURATION.md](ENV_CONFIGURATION.md) for detailed cookie instructions

#### No .env File

**Problem**: `SUBSTACK_USER not set in .env file`

**Solution**:
```bash
# Copy the example file
cp .env.example .env

# Edit with your credentials
nano .env  # or use any text editor
```

#### Empty Results

**Problem**: Scraper runs but finds 0 publications

**Possible Causes**:
1. **Cookie expired**: Get a fresh cookie from your browser
2. **Wrong URL**: Check that `SUBSTACK_USER` is correct in `.env`
3. **No subscriptions**: Make sure you have subscriptions on Substack
4. **Substack changed HTML**: File an issue on GitHub

### Performance Issues

#### Slow Performance

**Problem**: Scraping takes too long

**Solutions**:
```bash
# Increase parallel workers
python substack_reads.py --workers 10

# Enable caching (default, but verify you haven't disabled it)
python substack_reads.py  # without --no-cache

# Use parallel downloads (default)
python substack_reads.py  # without --no-parallel
```

#### Rate Limiting / 429 Errors

**Problem**: Getting 429 (Too Many Requests) errors

**Solutions**:
```bash
# Reduce workers
python substack_reads.py --workers 2

# Add delay between requests
python substack_reads.py --delay 2.0

# Use sequential downloads
python substack_reads.py --no-parallel
```

### Platform-Specific Issues

#### Windows Path Issues

**Problem**: File paths not working on Windows

**Solution**: The app uses `pathlib` which handles cross-platform paths automatically. If you have issues, make sure you're using forward slashes in `.env` paths or use raw strings.

#### macOS Certificate Errors

**Problem**: SSL certificate verification failed

**Solution**:
```bash
# Install certificates (Python 3.x)
/Applications/Python\ 3.x/Install\ Certificates.command

# Or update certifi
pip install --upgrade certifi
```

### Getting Help

If you're still having issues:

1. **Check logs**: Run with `--log-level DEBUG --log-file debug.log`
2. **Verify setup**: Make sure all installation steps were completed
3. **Test dependencies**: Run `python -c "import requests, bs4, dotenv; print('OK')"`
4. **File an issue**: Include Python version, OS, error messages, and debug logs

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
   - Author bio from Substack profile (4 points)
   - URL structure (2 points)
   - Page content (1.5 points)
   - Author field (1 point)

2. **40+ Categories**: tech, ai, crypto, startups, business, finance, marketing, news, politics, culture, law, health, science, writing, music, and more

3. **Smart Matching**:

   - Word boundary detection (prevents false positives)
   - Multi-word phrase support
   - Case-insensitive matching

4. **Automatic Author Discovery**: Fetches author bios from Substack profiles for intelligent categorization

5. **Fallback Strategies**: Contextual inference for publications with minimal metadata

### Example Results

```json
{
  "name": "Davey Havok",
  "author": "Davey Havok",
  "labels": ["music", "music-focused"]
},
{
  "name": "Legally Trans",
  "author": "Chase Strangio",
  "labels": ["culture", "culture-focused", "law", "law-focused", "politics"]
}
```

## License

MIT License - see LICENSE file for details

## Version History

- **v1.0.0** - Initial public release with intelligent categorization, modular architecture, and performance optimizations

---

**Built with ❤️ for Substack enthusiasts**
