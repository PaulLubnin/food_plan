from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Category, Customer, Recipe


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ["preview"]

    def preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" height="200px">')
