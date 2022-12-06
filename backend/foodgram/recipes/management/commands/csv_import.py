import csv
import os

import django.db.utils
from django.core.management.base import BaseCommand
from django.db import connection
from recipes.models import Ingredient


def read_csv(name_file):
    """Считывает данные из csv и возвращает список строк таблицы"""
    path = os.path.join('data/', name_file)
    with open(path, encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        return list(reader)


def load_data(model, name_file):
    """
    Загрузка данных по имени модели.
    """
    table = read_csv(name_file)
    model.objects.bulk_create(
        model(name=row[0], measurement_unit=row[1]) for row in table
    )


def del_data(model):
    """Удаляет данныее из таблицы"""
    model.objects.all().delete()
    with connection.cursor() as cursor:
        cursor.execute(
            'TRUNCATE TABLE recipes_ingredient RESTART IDENTITY CASCADE'
        )


class Command(BaseCommand):
    help = 'Импортирует data/ingredients.csv в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '-c',
            '--clear',
            action='store_true',
            help='Очищает таблицу recipes_ingredient'
        )

    def handle(self, *args, **options):
        try:
            if options['clear']:
                del_data(Ingredient)
                self.stdout.write(
                    self.style.SUCCESS('Ингредиенты удалены из базы данных'))
            else:
                load_data(Ingredient, 'ingredients.csv')
                self.stdout.write(
                    self.style.SUCCESS('Таблицы загружены в базу данных.'))
        except django.db.utils.IntegrityError as e:
            self.stdout.write(
                self.style.ERROR('Ошибка загрузки. База данных не пуста. '
                                 'Совпадение уникальных полей. "%s"' % e))
        except Exception as e:
            self.stdout.write(self.style.ERROR('Ошибка загрузки данных:'
                                               ' "%s"' % e))
