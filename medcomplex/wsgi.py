import os
import sys
import logging
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent
project_root = BASE_DIR.parent

# Add project root to Python path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medcomplex.settings')

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)
logger.debug("===== WSGI STARTUP =====")
logger.debug(f"Python version: {sys.version}")
logger.debug(f"Python path: {sys.path}")
logger.debug(f"Current directory: {os.getcwd()}")
logger.debug(f"BASE_DIR: {BASE_DIR}")
logger.debug(f"Project root: {project_root}")

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    logger.info("WSGI application loaded successfully")
except Exception as e:
    logger.exception("WSGI application failed to load")
    raise
