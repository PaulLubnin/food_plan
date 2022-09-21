from django.db import models
from django.core.validators import RegexValidator



class Category(models.Model):
    title = models.CharField('Название', max_length=150, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория блида'
        verbose_name_plural = 'Категории блюд'    


class Recipe(models.Model):
    title = models.CharField('Название', max_length=200)
    category = models.ManyToManyField(
        Category,
        related_name='recipes',
        verbose_name='Категории',
    )
    description = models.TextField('Описание', blank=True)
    instruction = models.TextField('Инструкция приготовления', blank=True)
    ingredients = models.TextField('Ингридиенты', blank=True)
    price = models.FloatField('Цена', blank=True, null=True)
    image = models.ImageField('Картинка', upload_to='images/', blank=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class Customer(models.Model):
    telegramm_id = models.IntegerField('Telegram ID')
    name = models.CharField('Имя', max_length=150)
    phone_number_regex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    phone_number = models.CharField(
        validators = [phone_number_regex],
        max_length = 16,
        unique = True,
        null=True)
    likes = models.ManyToManyField(
        Recipe,
        related_name='liked_users',
        verbose_name='Понравившееся рецерты',
        blank=True
    )
    dislikes = models.ManyToManyField(
        Recipe,
        related_name='disliked_users',
        verbose_name= 'Не понравившееся рецерты',
        blank=True
    )

    def __str__(self):
        return f'{self.name} {self.telegramm_id}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
