import logging
import sys
from logging.handlers import RotatingFileHandler


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),  # Console
        RotatingFileHandler("app.log", maxBytes=5_000_000, backupCount=5),  # File
    ],
)

logger = logging.getLogger(__name__)
