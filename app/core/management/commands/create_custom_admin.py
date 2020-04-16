from django.contrib.auth import get_user_model
from django.core.management import CommandError
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = 'create/update a superuser with password'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('--password', dest='password', default=None)
        parser.add_argument('--email', dest='email', default=None)

    def handle(self, *args, **kwargs):
        password = kwargs.get('password')
        email = kwargs.get('email')

        if not password or not email:
            raise CommandError("--username and --email are required")

        User = get_user_model()
        try:
            # TODO: change password
            if User.objects.filter(email=email).exists():
                self.stdout.write("Superuser %s already exists" % email)
            else:
                User.objects.create_superuser(email=email, password=password)
        except IntegrityError as e:
            self.stdout.write(self.style.WARNING(e.__repr__()))

        self.stdout.write(self.style.SUCCESS('Superuser %s created!' % email))
