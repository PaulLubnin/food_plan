from django.contrib import admin
from .models import Category, User, Recipe


@admin.register(Category)
class ComplaintAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class ComplaintAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class ComplaintAdmin(admin.ModelAdmin):
    pass
