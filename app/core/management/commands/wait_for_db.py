import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to pause exec until database is available"""

    def handle(self, *args, **kwargs):
        self.stdout.write('Waiting for database...')
        success = False
        while not success:
            try:
                with connections['default'].cursor() as cursor:
                    cursor.execute("select 1")
                    one = cursor.fetchone()[0]
                    if one == 1:
                        success = True
            except OperationalError:
                self.stdout.write('Database is unavailable, waiting 1 sec...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available!'))
