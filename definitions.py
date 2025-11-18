# definitions.py
#
# DEPRECATED: This file is maintained for backward compatibility only.
# New code should import from:
#   - modules.config (Config class, headers, URL)
#   - modules.categories (KEYWORD_CATEGORIES)
#
# This file will be removed in a future version.

import os
from pathlib import Path

# Re-export from new locations for backward compatibility
from modules.config import Config
from modules.categories import KEYWORD_CATEGORIES

# Deprecated: Use Config.get_headers() instead
HEADERS = Config.get_headers()

# Deprecated: Use Config.substack_user instead
SUBSTACK_USER = Config.substack_user

# Deprecated: Use Config.get_substack_url() instead
SUBSTACK_URL = Config.get_substack_url()

# Note: KEYWORD_CATEGORIES is re-exported from modules.categories
# Use: from modules.categories import KEYWORD_CATEGORIES
