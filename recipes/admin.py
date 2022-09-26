from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.safestring import mark_safe

from .models import Category, Customer, Recipe

from environs import Env
from telegram import Bot

env = Env()
env.read_env()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    actions = ['send_notification']

    def send_notification(self, request, queryset):
        if 'apply' in request.POST:
            bot = Bot(token=env('TELEGRAM_TOKEN'))
            notification = request.POST.get('notification')
            selected_ids = request.POST.getlist('_selected_action')
            for customer in Customer.objects.filter(id__in=selected_ids):
                bot.send_message(text=notification, chat_id=customer.telegramm_id)
            return HttpResponseRedirect(request.get_full_path())
        return render(
            request,
            'admin/notification_intermediate.html',
            context={'customers': queryset}
        )

    send_notification.short_description = 'Послать сообщение'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ["preview"]

    def preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" height="200px">')
