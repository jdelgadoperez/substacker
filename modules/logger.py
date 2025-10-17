"""
Logging configuration and utilities for the Substack scraper.
"""

import logging
import sys
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output"""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        if hasattr(sys.stderr, "isatty") and sys.stderr.isatty():
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    level: str = "INFO", log_file: Optional[str] = None, quiet: bool = False
):
    """
    Configure logging for the application

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to
        quiet: If True, suppress console output (errors only)
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(numeric_level)

    # Console handler
    if not quiet:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)

        # Use colored formatter for console
        console_formatter = ColoredFormatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    else:
        # In quiet mode, only show errors
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.ERROR)
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file

        # Use detailed formatter for file
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class ProgressBar:
    """Simple progress bar for terminal output"""

    def __init__(self, total: int, description: str = "", width: int = 50):
        """
        Initialize progress bar

        Args:
            total: Total number of items
            description: Description to show before the bar
            width: Width of the progress bar in characters
        """
        self.total = total
        self.current = 0
        self.description = description
        self.width = width
        self.logger = get_logger(__name__)
        self.last_line_length = 0  # Track last line length to clear properly

    def update(self, n: int = 1, status: str = ""):
        """
        Update progress bar

        Args:
            n: Number of items to increment by
            status: Optional status message to show
        """
        self.current += n
        if self.current > self.total:
            self.current = self.total

        # Calculate progress
        progress = self.current / self.total if self.total > 0 else 1.0
        filled = int(self.width * progress)
        bar = "█" * filled + "░" * (self.width - filled)

        # Build status line - truncate status to prevent line wrapping
        percent = progress * 100
        if status:
            # Limit status to 40 characters to prevent overflow
            status = status[:40]
            status_msg = f" {status}"
        else:
            status_msg = ""

        line = f"\r{self.description} |{bar}| {self.current}/{self.total} ({percent:.1f}%){status_msg}"

        # Pad with spaces to clear previous line if it was longer
        if len(line) < self.last_line_length:
            line += " " * (self.last_line_length - len(line))

        self.last_line_length = len(line)

        # Print without newline
        sys.stdout.write(line)
        sys.stdout.flush()

        # Add newline when complete
        if self.current >= self.total:
            sys.stdout.write("\n")
            sys.stdout.flush()

    def finish(self):
        """Complete the progress bar"""
        if self.current < self.total:
            self.current = self.total
            self.update(0)
