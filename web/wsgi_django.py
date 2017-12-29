# entry point for the Django loop
import os
import sys
from .__init__ import PROJECT_NAME

os.environ.update(DJANGO_SETTINGS_MODULE= (PROJECT_NAME + '.settings'))
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()