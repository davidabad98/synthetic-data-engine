import logging
import logging.config
import os
from pathlib import Path


def setup_logging():
    """Initialize logging configuration for the entire application"""
    config_path = (
        Path(__file__).resolve().parent.parent.parent / "config" / "logging.conf"
    )
    log_dir = Path(__file__).resolve().parent.parent.parent / "logs"

    # Create logs directory
    log_dir.mkdir(exist_ok=True, parents=True)

    # Load logging configuration
    logging.config.fileConfig(
        config_path, defaults={"logdir": str(log_dir)}, disable_existing_loggers=False
    )

    # Optional: Capture warnings from warnings module
    logging.captureWarnings(True)
