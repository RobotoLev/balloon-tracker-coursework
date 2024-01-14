from django.apps import AppConfig

import os


class MainAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main_app'

    def ready(self):  # Start timed jobs when the system is ready
        from . import jobs
        if os.environ.get('RUN_MAIN', None) != 'true':
            jobs.start_scheduler()
