import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, LabeledPrice, ReplyKeyboardMarkup
import os

from django.core.exceptions import ValidationError
from recipes.models import Customer, Recipe, Category

logger = logging.getLogger(__name__)

(
    AWAIT_AGREEMENT,
    AWAIT_NAME,
    AWAIT_PHONE,
    AWAIT_MENU_CHOICE,
    AWAIT_CATEGORY_CHOICE,
    AWAIT_RECIPE_ACTION,
    AWAIT_FAVORITES_ACTION,
    AWAIT_PAYMENT,
    HANDLE_PAYMENT,
    FINISH
) = range(10)


def start(update, context, again=False):
    try:
        customer = Customer.objects.get(telegramm_id=update.message.from_user.id)
        if customer.name and customer.phone_number:
            return show_menu(update, context)
        elif customer.name:
            return request_contact(update, context)
    except Customer.DoesNotExist:
        pass
    keyboard = []
    keyboard.append([
        InlineKeyboardButton('✅ Принять', callback_data='agree'),
        InlineKeyboardButton('❌ Отклонить', callback_data='disagree'),
    ])
    caption = 'Чтобы продолжить, вы должны согласиться с политикой обработки персональных данных'
    if not again:
        caption = f'Вас приветствует FoodPlan! {caption}'
    file_path = os.path.join('staticfiles', 'agreement.pdf')
    with open(file_path, 'rb') as agreement_pdf_file:
        context.bot.send_document(
            update.message.from_user.id,
            agreement_pdf_file,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    return AWAIT_AGREEMENT


def handle_agreement(update, context):
    query = update.callback_query
    query.message.delete()
    if query.data == 'agree':
        query.message.reply_text(
            'Пожалуйста, напишите ваши имя и фамилию'
        )
        return AWAIT_NAME
    update.message = query.message
    update.message.from_user = query.from_user
    start(update, context, again=True)


def handle_name(update, context):
    customer, created = Customer.objects.get_or_create(telegramm_id=update.message.from_user.id)
    customer.name = update.message.text
    customer.save()
    return request_contact(update, context)


def request_contact(update, context):
    keyboard = [[KeyboardButton('☎ Передать контакт', request_contact=True)]]
    update.message.reply_text(
        'Укажите ваш телефон, нажав на кнопку «Передать контакт», или текстом в формате +79123456789',
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return AWAIT_PHONE


def handle_phone(update, context):
    if update.message.contact:
        phone_number = update.message.contact.phone_number
    else:
        phone_number = update.message.text
    customer, created = Customer.objects.get_or_create(telegramm_id=update.message.from_user.id)
    customer.phone_number = phone_number
    try:
        customer.full_clean()
    except ValidationError:
        context.bot.delete_message(update.message.from_user.id, int(update.message.message_id) - 1)
        update.message.reply_text('Неверный формат телефона')
        return request_contact(update, context)
    customer.save()
    context.bot.delete_message(update.message.from_user.id, int(update.message.message_id) - 1)
    return show_menu(update, context)


def show_menu(update, context, back=False):
    if update.callback_query:
        message = update.callback_query.message
    else:
        message = update.message
    keyboard = []
    keyboard.append([
        InlineKeyboardButton('🧑‍🍳 Случайный рецепт', callback_data='recipe'),
        InlineKeyboardButton('🍳 Выбрать раздел', callback_data='categories')
    ])
    keyboard.append([
        InlineKeyboardButton('💖 Избранное', callback_data='favorites'),
    ])
    if back:
        message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        message.reply_text(
            'Уже голодны?',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    return AWAIT_MENU_CHOICE


def return_to_menu(update, context):
    return show_menu(update, context, back=True)


def return_to_menu_from_favorites(update, context):
    query = update.callback_query
    query.message.delete()
    return show_menu(update, context)


def show_categories(update, context):
    query = update.callback_query
    keyboard = []
    for category in Category.objects.all():
        keyboard.append([InlineKeyboardButton(category.title, callback_data=f'category-{category.id}')])
    query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
    return AWAIT_CATEGORY_CHOICE


def show_recipe(update, context, after_dislike=False):
    query = update.callback_query
    if query.message.text == 'Уже голодны?' or 'recipe-' in query.data:
        query.message.delete()
    else:
        query.message.edit_reply_markup(reply_markup=None)
    if after_dislike:
        query.message.delete()
        context.bot.delete_message(query.from_user.id, int(query.message.message_id) - 1)
    recipe_is_favorite = False
    customer = Customer.objects.get(telegramm_id=query.from_user.id)
    if not customer.subscriber and customer.recipes_shown >= 3:
        return offer_subscription(update, context)
    if 'recipe-' in query.data:
        recipe_is_favorite = True
        recipe = Recipe.objects.get(id=int(query.data.replace('recipe-', '')))
    else:
        recipes = Recipe.objects.all()
        if 'category' in query.data:
            recipes = recipes.filter(category__id=int(query.data.replace('category-', '')))
        recipe = recipes.exclude(disliked_users=customer).order_by('?').first()
    if not recipe:
        query.message.reply_text('По этому критерию рецептов не найдено')
        return show_menu(update, context)
    if not recipe.image:
        image_filename = os.path.join('staticfiles', 'default.jpg')
    else:
        image_filename = recipe.image.path
    keyboard = []
    if recipe_is_favorite:
        keyboard.append([
            InlineKeyboardButton('❌ Удалить из избранного', callback_data=f'dislike-{recipe.id}'),
            InlineKeyboardButton('🏠 В меню', callback_data='menu'),
        ])
    else:
        keyboard.append([
            InlineKeyboardButton('👍 Буду готовить!', callback_data=f'like-{recipe.id}'),
            InlineKeyboardButton('👎 Хочу другой рецепт', callback_data=f'dislike-{recipe.id}'),
        ])
        keyboard.append([InlineKeyboardButton('🏠 В меню', callback_data='menu')])
    with open(image_filename, 'rb') as image_file:
        query.message.reply_photo(
            image_file,
            caption=recipe.title
        )
    query.message.reply_text(
        f'{recipe.ingredients.strip()}\n\n{recipe.instruction.strip()}',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    customer.recipes_shown += 1
    customer.save()
    return AWAIT_RECIPE_ACTION


def handle_recipe_action(update, context):
    query = update.callback_query
    customer = Customer.objects.get(telegramm_id=query.from_user.id)
    if 'dislike' in query.data:
        recipe_id = int(query.data.replace('dislike-', ''))
        recipe = Recipe.objects.get(id=recipe_id)
        if customer in recipe.liked_users.all():
            customer.likes.remove(recipe)
            query.answer('Рецепт удалён из избранного')
        else:
            customer.dislikes.add(recipe)
            query.answer('Рецепт добавлен в чёрный список')
        return show_recipe(update, context, after_dislike=True)
    elif 'like' in query.data:
        recipe_id = int(query.data.replace('like-', ''))
        customer.likes.add(Recipe.objects.get(id=recipe_id))
        query.answer('Рецепт добавлен в избранное')
        keyboard = []
        keyboard.append([
            InlineKeyboardButton('🧑‍🍳 Другой рецепт', callback_data='recipe'),
            InlineKeyboardButton('🏠 В меню', callback_data='menu'),
        ])
        query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
    return AWAIT_RECIPE_ACTION


def show_favorites(update, context):
    products_per_page = 8
    query = update.callback_query
    if query.message.text == 'Уже голодны?':
        query.message.delete()
    else:
        query.message.edit_reply_markup(reply_markup=None)
    customer = Customer.objects.get(telegramm_id=query.from_user.id)
    page = 0
    if 'page' in query.data:
        page = int(query.data.replace('page-', ''))
    keyboard = []
    recipes = Recipe.objects.filter(liked_users=customer).order_by('title')
    for recipe in recipes[page * products_per_page:(page + 1) * products_per_page]:
        keyboard.append([InlineKeyboardButton(recipe.title, callback_data=f'recipe-{recipe.id}')])
    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(InlineKeyboardButton('⬅️ Предыдущие', callback_data=f'page-{page - 1}'))
    if len(recipes) > (page + 1) * products_per_page:
        pagination_buttons.append(InlineKeyboardButton('Следующие ➡️', callback_data=f'page-{page + 1}'))
    keyboard.append(pagination_buttons)
    keyboard.append([InlineKeyboardButton('🏠 В меню', callback_data='menu')])
    query.message.reply_text(
        'Вы поставили лайк этим блюдам:',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return AWAIT_FAVORITES_ACTION


def offer_subscription(update, context):
    query = update.callback_query
    keyboard = []
    keyboard.append([
        InlineKeyboardButton('💳 Оплатить', callback_data='pay'),
        InlineKeyboardButton('🏠 В меню', callback_data='menu'),
    ])
    query.message.reply_text(
        'Вы достигли лимита рецептов в пробном режиме. Пожалуйста, оформите подписку',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return AWAIT_PAYMENT


def offer_payment(update, context):
    token = context.bot_data['payment_provider_token']
    query = update.callback_query
    prices = [LabeledPrice('Подписка на сервис Foodplan', 19900)]
    context.bot.send_invoice(query.from_user.id, 'Оплата подписки', ' ', 'foodplan_payment', token, 'RUB', prices)
    return AWAIT_PAYMENT


def handle_precheckout(update, context):
    query = update.pre_checkout_query
    if query.invoice_payload != 'foodplan_payment':
        query.answer(ok=False, error_message='В процессе оплаты произошла ошибка')
    else:
        query.answer(ok=True)
    return AWAIT_PAYMENT


def handle_successful_payment(update, context):
    customer = Customer.objects.get(telegramm_id=update.message.from_user.id)
    customer.subscriber = True
    customer.save()
    keyboard = [[InlineKeyboardButton('🏠 В меню', callback_data='menu')]]
    update.message.reply_text(
        'Спасибо за оплату! Теперь вы можете смотреть неограниченное число рецептов',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return HANDLE_PAYMENT
