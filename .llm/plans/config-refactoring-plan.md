# Config Refactoring Plan

**Date**: 2025-11-18
**Status**: In Progress
**Objective**: Consolidate and clean up configuration management across the substacker codebase

## Current State Analysis

### Configuration Files
1. **definitions.py** (734 lines)
   - Environment variable loading (`.env`)
   - HTTP headers with session cookie
   - Substack URL generation
   - KEYWORD_CATEGORIES dictionary (~700 lines, 40+ categories)

2. **modules/config.py** (40 lines)
   - Config class with feature flags
   - Performance settings (workers, timeouts, retries)
   - Output paths (hardcoded to ~/projects/sandbox/exports)
   - CACHE_EXPIRY_DAYS at module level

### Problems Identified

1. **Scattered Configuration**: Config split between two files with unclear ownership
2. **Bloated definitions.py**: Single file contains env vars, network config, AND domain knowledge (keywords)
3. **Mixed Concerns**: Business logic (keyword categories) mixed with environment config
4. **Inconsistent Access Patterns**: Some config via global constants, some via Config class
5. **Hardcoded Paths**: Output directories hardcoded instead of derived from project root

## Proposed Solution

### New Structure

```
substacker/
├── modules/
│   ├── config.py          # Unified configuration (expanded)
│   ├── categories.py      # Keyword categories (new)
│   └── ...
└── definitions.py         # DEPRECATED (keep for backward compatibility, mark for removal)
```

### 1. Create `modules/categories.py`

**Purpose**: Store domain knowledge (keyword categories for auto-labeling)

**Contents**:
- KEYWORD_CATEGORIES dictionary
- Helper functions for category management (if needed in future)

**Rationale**: Separates business logic from configuration. Categories are domain knowledge, not config.

### 2. Expand `modules/config.py`

**New Config class structure**:

```python
class Config:
    """Unified configuration for Substack scraper"""

    # === Environment Variables (from .env) ===
    substack_user: str
    substack_cookie: str
    substack_url: str

    # === Network Settings ===
    headers: dict
    timeout: int = 10
    max_retries: int = 2
    rate_limit_delay: float = 1.0

    # === Performance Settings ===
    max_workers: int = 5
    parallel_downloads: bool = True
    use_cache: bool = True
    skip_if_labeled: bool = True

    # === Feature Flags ===
    download_images: bool = True
    extract_metadata: bool = False
    validate_data: bool = True
    analyze_content: bool = True

    # === Paths (derived from project root) ===
    project_root: Path
    images_folder: Path
    exports_folder: Path
    cache_dir: Path

    # === Label Filtering ===
    include_labels: Optional[list[str]] = None
    exclude_labels: Optional[list[str]] = None

    # === Cache Settings ===
    cache_expiry_days: int = 7
```

**Key improvements**:
- Single source of truth for ALL configuration
- Environment variables loaded into Config class
- Paths derived from project root (portable, not hardcoded)
- Clear grouping by concern
- Class methods for initialization and validation

### 3. Deprecate `definitions.py`

**Short-term approach**:
- Keep file for backward compatibility
- Re-export from modules.config and modules.categories
- Add deprecation warnings/comments

**Long-term approach**:
- Remove entirely in future version
- Update all imports to use new modules

## Implementation Steps

### Phase 1: Create New Modules (No Breaking Changes)

1. **Create `modules/categories.py`**
   - Copy KEYWORD_CATEGORIES from definitions.py
   - Add module docstring
   - No other changes

2. **Expand `modules/config.py`**
   - Move env var loading into Config class
   - Move HTTP headers into Config class
   - Move URL generation into Config class
   - Add class method `Config.load()` for initialization
   - Add class method `Config.from_env()` for env var loading
   - Derive paths from project root instead of hardcoding
   - Move CACHE_EXPIRY_DAYS into Config class

### Phase 2: Update Imports

3. **Update module imports**
   - modules/labeling.py: Import KEYWORD_CATEGORIES from categories
   - modules/scraper.py: Import headers/URL from Config
   - modules/cache.py: Import CACHE_EXPIRY_DAYS from Config
   - Any other modules using definitions.py

4. **Update main script (substack_reads.py)**
   - Import from new locations
   - Initialize Config properly
   - Test all CLI arguments still work

### Phase 3: Update definitions.py (Backward Compatibility)

5. **Make definitions.py a compatibility shim**
   - Import and re-export from new modules
   - Add deprecation comments
   - Keep for external users/scripts

### Phase 4: Documentation & Testing

6. **Update documentation**
   - README.md: Update architecture section
   - ENV_CONFIGURATION.md: Update config file locations
   - CLAUDE.md: Update developer guidance
   - Inline comments in code

7. **Test thoroughly**
   - Run with default args
   - Run with all CLI flags
   - Test cache functionality
   - Test label filtering
   - Verify no regressions

## Success Criteria

- [ ] All configuration in one logical place (Config class)
- [ ] Keyword categories separated into own module
- [ ] No hardcoded paths (derive from project root)
- [ ] All existing functionality works unchanged
- [ ] Tests pass (if any exist)
- [ ] Documentation updated
- [ ] Code is more maintainable and clear

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking existing imports | Keep definitions.py as compatibility shim |
| Config initialization order issues | Use explicit Config.load() method |
| Path resolution on different systems | Use pathlib.Path and derive from __file__ |
| Forgot to update an import | Grep for "from definitions import" |

## Future Enhancements (Out of Scope)

- Config validation with pydantic or similar
- Config file (.toml/.yaml) support
- Multiple config profiles (dev/prod)
- Environment-specific overrides
- Config hot-reloading

## Notes

- Prioritize backward compatibility over perfection
- Make changes incrementally with git commits
- Test after each phase
- Document as we go
