from django.core.management.base import BaseCommand
from recipes.models import Recipe, Category
import json
import requests
import os
from urllib.parse import urlparse
from os.path import splitext, basename


def image_download(url, path):
    response = requests.get(url)
    response.raise_for_status()
    with open(path, 'wb') as file:
        file.write(response.content)


class Command(BaseCommand):
    help = 'Зашрузить данные из data_recipies.json в БД'

    def handle(self, *args, **options):
        with open("data_recipes.json", "r", encoding="UTF-8") as file:
            file_contents = json.load(file)
        raw_recipes = file_contents

        path = os.path.join('media', 'images')
        os.makedirs(path, exist_ok=True)

        for num, raw_recipe in enumerate(raw_recipes):
            Category.objects.get_or_create(title=raw_recipe['category'])
            category = Category.objects.get(title=raw_recipe['category'])

            image_url = raw_recipe['image']
            url_parse = urlparse(image_url)
            image_name, image_ext = splitext(basename(url_parse.path))
            
            image_path = os.path.join(path, f'{image_name}_{num}{image_ext}')
            image_download(image_url, image_path)
            
            ingredients = ''
            for index, ingredient in enumerate(raw_recipe['ingredients'][0]):
                ingredients += f'{ingredient} - {raw_recipe["ingredients"][1][index]}\n'

            instruction = ''
            for index, point in enumerate(raw_recipe['instruction'][0]):
                instruction += f'{point}. {raw_recipe["instruction"][1][index]}\n\n'

            recipe = Recipe(
                title=raw_recipe['title'],
                description=raw_recipe['description'],
                instruction=instruction,
                ingredients=ingredients,
            )
            recipe.save()

            recipe.category.add(category)
