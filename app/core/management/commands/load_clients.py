import csv

from django.core.management import CommandError
from django.core.management.base import BaseCommand
from netaddr import IPAddress, EUI

from core.models import Client


class Command(BaseCommand):
    help = 'load client data from csv file'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('--filename', dest='filename', default=None)

    def handle(self, *args, **kwargs):
        if "filename" not in kwargs:
            raise CommandError("Command supports only one argument - filename")
        filename: str = kwargs['filename']
        if not filename.endswith(".csv"):
            raise CommandError("Only supported type for loading data is .csv")

        try:
            with open(filename, 'r') as fin:
                reader = csv.reader(fin, delimiter=';')
                for row in reader:
                    if row[0]:
                        ip = int(IPAddress(row[0]))
                    else:
                        ip = None
                    if row[1]:
                        mac = int(EUI(row[1]))
                    else:
                        mac = None
                    if mac:
                        client = Client.objects.get_or_create(mac=mac)[0]
                        if ip and not client.ip:
                            client.ip = ip
                        print(f"Added {EUI(client.mac)}")
                        client.save()
        except Exception as e:
            raise CommandError(e)

        print("Successfully load data to db")
