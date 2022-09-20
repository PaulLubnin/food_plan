from django.db import models
 

class Category(models.Model):
    title = models.CharField('Название', max_length=150)

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
    price = models.FloatField('Цена', blank=True)
    image = models.ImageField('Картинка', upload_to='images/')
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class User(models.Model):
    telegramm_id = models.IntegerField('Telegram ID')
    name = models.CharField('Имя', max_length=150)
    phone = models.CharField('Номер телефона', max_length=20)
    likes = models.ManyToManyField(
        Recipe,
        related_name='liked_users',
        verbose_name='Понравившееся рецерты',
        blank=True
    )
    dislikes = models.ManyToManyField(
        Recipe,
        related_name='disliked_users',
        verbose_name= 'Не понравившееся рецерт',
        blank=True
    )

    def __str__(self):
        return f'{self.name} {self.telegramm_id}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
