import json
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Загружает рецепты с сайта eda.ru'

    def add_arguments(self, parser):
        parser.add_argument(
            '-p', '--page',
            nargs='+',
            type=int,
            help='Номер страницы',
        )

    def handle(self, *args, **options):
        recipes_urls = get_lists_url(options['page'])
        recipes = get_recipes(recipes_urls)
        writes_json(recipes)


def get_lists_url(page_number: list):
    """Функция парсит урлы рецептов с сайта eda.ru и возвращает список из урлов."""

    urls_list = [f'https://eda.ru/recepty?page={number}' for number in range(page_number[0], page_number[1])]

    recipe_urls = []
    for url in urls_list:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        recipe_links = soup.findAll('a', class_='emotion-18hxz5k')
        for data in recipe_links:
            recipe_urls.append(f'https://eda.ru{data["href"]}')

    return recipe_urls


def get_category(recipe_url: str):
    """Функция парсит урл и возвращает из него категорию блюда."""

    url = urlparse(recipe_url)
    category = url.path.split('/')
    return category[2]


def get_recipe_text(bs4_soup):
    """Функция перебирает суп и возвращает список из текстовых данных."""

    elements_list = []
    for elem in bs4_soup:
        elements_list.append(elem.text)
    return elements_list


def get_recipe_image(bs4_soup):
    """Функция перебирает суп и возвращает список из ссылок на картинку"""

    elements_list = []
    for elem in bs4_soup:
        elements_list.append(elem.img['src'])
    return elements_list


def get_recipes(recipes_urls: list):
    """Функция собирает словарь из блюд."""

    recipes_list = []
    count_page = 0
    for url in recipes_urls:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        recipe_title = get_recipe_text(soup.findAll('h1', class_="emotion-gl52ge"))
        recipe_description = get_recipe_text(soup.findAll('span', class_="emotion-1x1q7i2"))
        image_dish = get_recipe_image(soup.findAll('div', class_="emotion-mrkurn"))
        ingredients_list = get_recipe_text(soup.findAll('div', class_="emotion-bjn8wh"))
        quantity_list = get_recipe_text(soup.findAll('span', class_="emotion-15im4d2"))
        step_list = get_recipe_text(soup.findAll('span', class_='emotion-bzb65q'))
        action_list = get_recipe_text(soup.findAll('span', class_='emotion-6kiu05'))

        recipe = {
            'title': recipe_title[0],
            'description': recipe_description,
            'ingredients': (ingredients_list, quantity_list),
            'instruction': (step_list, action_list),
            'category': get_category(url),
            'image': image_dish[0]
        }
        recipes_list.append(recipe)
        time.sleep(0.5)
        count_page += 1
        print(f'Загружен {count_page} рецепт')

    return recipes_list


def writes_json(array: list):
    """Функция записывает данные в json файл."""

    with open('data_recipes.json', 'w', encoding='utf8') as file:
        json.dump(array, file, ensure_ascii=False)
    print('Рецепты записаны в "data_recipes.json"')
