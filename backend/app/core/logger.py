import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Configures and returns a logger with the VaaniAi standard format.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent adding multiple handlers if get_logger is called repeatedly
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '[VAANIAI] %(levelname)s | %(asctime)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger