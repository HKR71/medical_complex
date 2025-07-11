# medcomplex/wsgi.py
import os
import sys
import logging

path = '/home/hakarsalih/medical_complex'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medcomplex.settings')

# Add logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    logging.info("WSGI application loaded successfully")
except Exception as e:
    logging.exception("WSGI application failed to load")
    raise
