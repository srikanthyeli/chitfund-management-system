import os
import logging
import logging.config
import logging.handlers
from pathlib import Path

def setup_logging():
    # Resolve the root of the backend to create logs/ directory
    current_file = Path(__file__).resolve()
    backend_root = current_file.parents[4]
    logs_dir = backend_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Programmatic configuration to ensure path to log file is correct
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    logging.basicConfig(level=logging.INFO)
    
    root_logger = logging.getLogger()
    # Remove default handlers to avoid duplicate log entries
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(console_handler)
    
    # Daily rotating file handler
    file_path = logs_dir / "app.log"
    file_handler = logging.handlers.TimedRotatingFileHandler(
        str(file_path),
        when="midnight",
        interval=1,
        backupCount=30
    )
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(file_handler)
    
    root_logger.setLevel(logging.INFO)

# Run setup
setup_logging()

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
