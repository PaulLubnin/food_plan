# Generated by Django 3.2.7 on 2022-09-22 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_recipe_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='dislikes',
            field=models.ManyToManyField(blank=True, related_name='disliked_users', to='recipes.Recipe', verbose_name='Непонравившееся рецерты'),
        ),
    ]
