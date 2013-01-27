import sys, os, logging
logger = logging.getLogger(__name__)

def setup():
    settings_dir = sys.argv[1]

    if len(sys.argv) < 2 or len(sys.argv) > 2 or not os.path.exists(settings_dir):
        logger.error('directory of settings file required, exitting')
        sys.exit(1)

    sys.path.append(settings_dir)

    from django.conf import settings
    from django.core.management import setup_environ
    setup_environ(settings)
