import logging
import sys

# -------------------- Universal Logger Setup --------------------
def get_logger(name: str = "app_logger", level: int = logging.INFO) -> logging.Logger:
    # Returns a configured logger instance that can be used across the project.

    # Parameters:
    #     name (str): Logger name.
    #     level (int): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    # Returns:
    #     logging.Logger: Configured logger instance.
    logger = logging.getLogger(name)  # Create or get existing logger
    logger.setLevel(level)  # Set the logging level

    if not logger.handlers:  # Prevent adding multiple handlers if imported multiple times
        # Console handler (prints logs to stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)  # Same logging level as logger

        # Log format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)

        # Attach handler to logger
        logger.addHandler(console_handler)

    return logger
