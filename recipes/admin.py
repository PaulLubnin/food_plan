from django.contrib import admin
from .models import Category, Customer, Recipe


@admin.register(Category)
class ComplaintAdmin(admin.ModelAdmin):
    pass


@admin.register(Customer)
class ComplaintAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class ComplaintAdmin(admin.ModelAdmin):
    pass
