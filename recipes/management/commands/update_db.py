from django.core.management.base import BaseCommand
from recipes.models import Recipe, Category
import json


class Command(BaseCommand):
    help = 'Зашрузить данные из data_recipies.json в БД'

    def handle(self, *args, **options):
        with open("data_recipies.json", "r", encoding="UTF-8") as file:
            file_contents = json.load(file)
        raw_recipes = file_contents

        for raw_recipe in raw_recipes:
            Category.objects.get_or_create(title='Тестовая')
            category = Category.objects.get(title='Тестовая')

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
