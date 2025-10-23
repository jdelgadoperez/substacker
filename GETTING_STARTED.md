# Getting Started with Substacker

A complete beginner's guide to setting up and running the Substack scraper.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Getting Your Substack Cookie](#getting-your-substack-cookie)
4. [Configuration](#configuration)
5. [Running the Scraper](#running-the-scraper)
6. [Understanding the Output](#understanding-the-output)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Python 3.7 or higher** - [Download Python](https://www.python.org/downloads/)
- **A Substack account** with subscriptions
- **A web browser** (Chrome, Firefox, Safari, or Edge)
- **Basic command line knowledge** (optional but helpful)

---

## Installation

### 1. Clone or Download the Repository

```bash
git clone https://github.com/yourusername/substacker.git
cd substacker
```

Or download and extract the ZIP file.

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:

- `requests` - For making web requests
- `beautifulsoup4` - For parsing HTML
- `python-dotenv` - For managing environment variables

---

## Getting Your Substack Cookie

The scraper needs your Substack session cookie to access your subscriptions. This is completely safe - the cookie stays on your computer and is never shared.

### Why Do I Need This?

Your Substack subscriptions are private to your account. The cookie proves to Substack that you're logged in, allowing the scraper to see your subscriptions list.

### Method 1: Using Browser Developer Tools (Recommended)

#### **Google Chrome / Microsoft Edge**

1. **Open Substack and Log In**

   - Go to [https://substack.com](https://substack.com)
   - Log in to your account
   - Navigate to your reads page: `https://substack.com/@yourusername/reads`

2. **Open Developer Tools**

   - Press `F12` on your keyboard
   - Or right-click anywhere on the page and select "Inspect"
   - Or use the menu: ⋮ (three dots) → More Tools → Developer Tools

3. **Go to the Network Tab**

   - Click the **Network** tab at the top of the Developer Tools panel
   - If you don't see any activity, refresh the page (`F5` or `Ctrl+R` / `Cmd+R`)

4. **Find a Request to Substack**

   - Look for any request to `substack.com` in the list
   - Click on it to select it
   - Good examples: `reads`, `api`, or any file starting with `@`

5. **Copy the Cookie Header**

   - In the right panel, scroll down to **Request Headers**
   - Find the line that says `cookie:` or `Cookie:`
   - Click on the value (the long string after `cookie:`)
   - Right-click and select **Copy value**

   Example of what you'll see:

   ```
   cookie: substack.sid=s%3A...; __cf_bm=...; cf_clearance=...
   ```

6. **Save the Cookie**
   - Keep this value - you'll need it in the next step

---

#### **Mozilla Firefox**

1. **Open Substack and Log In**

   - Go to [https://substack.com](https://substack.com)
   - Log in to your account
   - Navigate to your reads page

2. **Open Developer Tools**

   - Press `F12`
   - Or right-click → Inspect Element
   - Or Menu → More Tools → Web Developer Tools

3. **Go to the Network Tab**

   - Click the **Network** tab
   - Refresh the page if you don't see any requests

4. **Find a Substack Request**

   - Look for requests to `substack.com`
   - Click on one to open the details

5. **Copy the Cookie**
   - In the right panel, click the **Headers** tab
   - Scroll to **Request Headers**
   - Find the `Cookie` line
   - Right-click the value and select **Copy**

---

#### **Safari (Mac)**

1. **Enable Developer Menu** (if not already enabled)

   - Safari → Preferences → Advanced
   - Check "Show Develop menu in menu bar"

2. **Open Substack and Log In**

   - Go to [https://substack.com](https://substack.com)
   - Log in and go to your reads page

3. **Open Web Inspector**

   - Press `Cmd+Option+I`
   - Or Develop → Show Web Inspector

4. **Go to Network Tab**

   - Click the **Network** tab
   - Refresh the page

5. **Find Request and Copy Cookie**
   - Click on any `substack.com` request
   - Look for **Request Headers** in the details
   - Find the `Cookie` line and copy its value

---

### Method 2: Using Browser Console (Quick Method)

This method is faster but gives you ALL cookies (which is fine, but might include unnecessary ones).

1. **Open Substack and Log In**

   - Go to [https://substack.com](https://substack.com)
   - Make sure you're logged in

2. **Open Console**

   - Press `F12` to open Developer Tools
   - Click the **Console** tab

3. **Run This Command**

   - Type or paste: `document.cookie`
   - Press `Enter`

4. **Copy the Output**
   - You'll see a long string like:
     ```
     "substack.sid=s%3A...; __cf_bm=...; cf_clearance=...; ..."
     ```
   - Select and copy this entire string (without the outer quotes)

---

## Configuration

### 1. Create Your Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

### 2. Edit the .env File

Open `.env` in any text editor and fill in your values:

```bash
# Your Substack username (the part after @ in your profile URL)
SUBSTACK_USER="@yourusername"

# Paste your cookie here (inside the quotes)
SUBSTACK_COOKIE="substack.sid=s%3A...; __cf_bm=...; cf_clearance=..."
```

**Important:**

- Keep the quotes around the cookie value
- Don't add extra spaces
- The cookie should be one long line

### Example

If your Substack profile is `https://substack.com/@johndoe`, your `.env` should look like:

```bash
SUBSTACK_USER="@johndoe"
SUBSTACK_COOKIE="substack.sid=s%3A1234abcd...; __cf_bm=5678efgh..."
```

---

## Running the Scraper

### Basic Usage

Run the scraper with default settings:

```bash
python substack_reads.py
```

You should see:

```
Scraping publications... ████████████████████ 50/50 (100%)
Downloaded 50 publication icons
Exported to: exports/substack_reads.json
Exported to: exports/substack_reads.csv
```

### Common Options

```bash
# Get more details
python substack_reads.py --detailed

# Include rich metadata (descriptions, subscriber counts)
python substack_reads.py --metadata

# Run quietly (only show errors)
python substack_reads.py --quiet

# Skip image downloads (faster)
python substack_reads.py --no-images
```

See [CLI_REFERENCE.md](CLI_REFERENCE.md) for all options.

---

## Understanding the Output

### Files Created

After running, you'll find:

```
substacker/
├── exports/
│   ├── substack_reads.json    # Full data in JSON format
│   └── substack_reads.csv     # Spreadsheet-friendly format
└── images/
    ├── Publication1.png        # Downloaded publication icons
    ├── Publication2.jpg
    └── ...
```

### JSON Structure

Each publication has this structure:

```json
{
	"name": "Tech Newsletter",
	"author": "Jane Doe",
	"link": "https://technewsletter.substack.com",
	"icon": "/path/to/image.png",
	"is_paid": false,
	"subscription_status": "Subscribed",
	"labels": ["tech", "free", "subscribed"]
}
```

### CSV Format

The CSV file can be opened in Excel, Google Sheets, or any spreadsheet application. Columns include:

- Name
- Author
- Link
- Is Paid (TRUE/FALSE)
- Subscription Status
- Labels (comma-separated)

---

## Troubleshooting

### "Cookie not found" Error

**Problem:** The `.env` file is missing or `SUBSTACK_COOKIE` is not set.

**Solution:**

1. Make sure `.env` file exists in the same folder as `substack_reads.py`
2. Check that you've added `SUBSTACK_COOKIE="..."` to the file
3. Make sure the cookie is inside quotes

---

### "Authentication Failed" Error

**Problem:** Your cookie is expired or invalid.

**Solution:**

1. Get a fresh cookie following the steps above
2. Replace the old cookie in your `.env` file
3. Try again

**Note:** Cookies typically expire after a few days. You'll need to update them periodically.

---

### "No Publications Found" Error

**Problem:** The scraper couldn't find any subscriptions.

**Possible causes:**

1. Wrong `SUBSTACK_USER` - check your username
2. You don't have any subscriptions yet
3. Substack changed their page structure (file an issue on GitHub)

**Solution:**

1. Verify your username: go to [substack.com](https://substack.com), look at your profile URL
2. Make sure you have at least one subscription
3. Try using `--detailed` flag to see more information

---

### "Module Not Found" Error

**Problem:** Python dependencies not installed.

**Solution:**

```bash
pip install -r requirements.txt
```

If that doesn't work:

```bash
pip3 install -r requirements.txt
```

---

### Slow Performance

**Problem:** Downloads are taking a long time.

**Solution:**

```bash
# Use more parallel workers
python substack_reads.py --workers 10

# Skip images for faster data extraction
python substack_reads.py --no-images
```

---

### Rate Limiting / 429 Errors

**Problem:** Substack is blocking requests (too many too fast).

**Solution:**

```bash
# Slow down requests
python substack_reads.py --delay 2.0 --workers 2
```

---

## Next Steps

Once you have the scraper working:

1. **Explore the data** - Open `exports/substack_reads.json` to see your subscriptions
2. **Customize labels** - Use `--include-labels` or `--exclude-labels` to filter
3. **Automate it** - Set up a cron job or scheduled task to run daily
4. **Extend it** - The code is modular and easy to customize

## Getting Help

- **Documentation:** Check the other `.md` files in this repo
- **Issues:** Found a bug? [Open an issue](https://github.com/yourusername/substacker/issues)
- **Questions:** See the [FAQ section](README.md#troubleshooting) in the main README

---

**Happy scraping! 🚀**
