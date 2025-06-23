import logging

LOG_ENABLED = True

def setup_logging():
    if LOG_ENABLED:
        logging.basicConfig(level=logging.INFO, format="%(message)s")
    else:
        logging.disable(logging.CRITICAL)  # Disabilita TUTTI i logging

setup_logging()
logger = logging.getLogger(__name__)