from django.core.management.base import BaseCommand
from ...utils.utils import create_tokens_from_dict
import json
class Command(BaseCommand):
    help = 'Import tokens from a dictionary'

    def add_arguments(self, parser):
        parser.add_argument('dict_path', type=str, help='Path to the dictionary file')

    def handle(self, *args, **options):
        dict_path = options['dict_path']
        with open(dict_path, 'r') as f:
            dict_data = json.load(f)
        create_tokens_from_dict(dict_data)
        self.stdout.write(self.style.SUCCESS('Tokens imported successfully.'))