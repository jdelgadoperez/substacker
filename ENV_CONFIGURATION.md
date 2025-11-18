# Environment Configuration

## Overview

The Substack scraper uses environment variables for sensitive configuration like authentication cookies and API tokens. This keeps credentials separate from code and out of version control.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `requests` - HTTP library for web scraping
- `beautifulsoup4` - HTML parsing
- `python-dotenv` - Environment variable management

### 2. Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

### 3. Configure Your Credentials

Edit `.env` and fill in your actual values:

```bash
# Substack Configuration (Required)
SUBSTACK_USER="@your_username"
SUBSTACK_COOKIE="your_actual_cookie_here"
```

## Getting Your Substack Cookie

The scraper needs your Substack session cookie to access your subscriptions.

### Steps:

1. **Log into Substack**
   - Go to https://substack.com
   - Log in with your account

2. **Open Developer Tools**
   - Chrome/Edge: Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
   - Firefox: Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
   - Safari: Enable Developer menu in Preferences, then press `Cmd+Option+I`

3. **Find Cookies**
   - Go to the **Application** tab (Chrome/Edge) or **Storage** tab (Firefox)
   - Navigate to **Cookies** → `https://substack.com`
   - You'll see a list of cookies

4. **Copy Cookie String**

   **Option A: Manual (Recommended)**
   - Look for these important cookies:
     - `substack.sid` (session ID)
     - `__cf_bm` (Cloudflare bot management)
     - `cf_clearance` (Cloudflare clearance)
     - `AWSALBTG` and `AWSALBTGCORS` (load balancer)
   - Copy each cookie in the format: `name=value`
   - Combine them with semicolons: `cookie1=value1; cookie2=value2; cookie3=value3`

   **Option B: Browser Console**
   - Go to the **Console** tab
   - Type: `document.cookie`
   - Press Enter
   - Copy the entire output string

5. **Add to .env File**

   Paste the cookie string into your `.env` file:
   ```
   SUBSTACK_COOKIE="substack.sid=s%3A...; __cf_bm=...; cf_clearance=..."
   ```

### Cookie Expiration

Cookies expire after some time. If the scraper stops working:
- You'll see authentication errors
- Get a fresh cookie following the steps above
- Update your `.env` file

**Note**: Session cookies typically last 1-7 days depending on Substack's settings.

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SUBSTACK_COOKIE` | Your Substack session cookie | `substack.sid=s%3A...` |

### Optional Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SUBSTACK_USER` | Your Substack username | `@yourusername` |

## Security Best Practices

### ✅ Do:
- Keep `.env` file local (it's in `.gitignore`)
- Use `.env.example` as a template for others
- Rotate cookies regularly
- Use environment variables for all sensitive data

### ❌ Don't:
- Commit `.env` to version control
- Share your `.env` file
- Hardcode cookies in source code
- Share screenshots containing cookies

## Troubleshooting

### "Cookie not found" Error

**Problem**: `SUBSTACK_COOKIE` is not set in `.env`

**Solution**:
1. Make sure `.env` file exists
2. Check that `SUBSTACK_COOKIE` is defined
3. Ensure the cookie value is in quotes

### "Authentication failed" Error

**Problem**: Cookie is invalid or expired

**Solution**:
1. Get a fresh cookie from your browser
2. Update `.env` file
3. Try again

### "python-dotenv not found" Error

**Problem**: Dependencies not installed

**Solution**:
```bash
pip install -r requirements.txt
```

## How It Works

### Loading Environment Variables

The `modules/config.py` file automatically loads environment variables:

```python
from dotenv import load_dotenv
from pathlib import Path

# Load .env from the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
env_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=env_path)

# Config class with environment variables
class Config:
    substack_user: str = os.getenv("SUBSTACK_USER", "")
    substack_cookie: str = os.getenv("SUBSTACK_COOKIE", "")

    @classmethod
    def get_headers(cls) -> dict:
        return {
            "User-Agent": "...",
            "Cookie": cls.substack_cookie,
        }
```

**Note**: `definitions.py` is deprecated and maintained only for backward compatibility. New code should import from `modules.config`.

### Fallback Behavior

If `python-dotenv` is not installed:
- The script falls back to system environment variables
- You can set variables manually: `export SUBSTACK_COOKIE="..."`
- Or use a `.env` loader from your shell

## Development vs Production

### Development

Use `.env` file for local development:
```bash
# In .env
SUBSTACK_COOKIE="dev_cookie_here"
```

### Production/CI

Use system environment variables:
```bash
# Set environment variable
export SUBSTACK_COOKIE="prod_cookie_here"

# Run script
python substack_reads.py
```

### Docker

```dockerfile
# Dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "substack_reads.py"]
```

```bash
# Run with environment variables
docker run -e SUBSTACK_COOKIE="..." substack-scraper
```

## Multiple Environments

Create separate `.env` files for different environments:

```bash
.env.dev       # Development
.env.staging   # Staging
.env.prod      # Production
```

Load specific environment:
```bash
# In Python
load_dotenv('.env.dev')
```

## Migration Notes

### Why Environment Variables?

**Hardcoded Approach** (not recommended):
```python
HEADERS = {
    "Cookie": "hardcoded_cookie_value_here"
}
```

**Problems**:
- Cookie visible in source code
- Gets committed to Git
- Hard to rotate
- Security risk

**Environment Variable Approach** (recommended):
```python
# In modules/config.py
class Config:
    substack_cookie: str = os.getenv("SUBSTACK_COOKIE", "")

    @classmethod
    def get_headers(cls) -> dict:
        return {"Cookie": cls.substack_cookie}
```

**Benefits**:
- Cookie not in source code
- Not committed to Git (`.env` is gitignored)
- Easy to rotate (just update `.env`)
- Secure and flexible
- Centralized configuration management
