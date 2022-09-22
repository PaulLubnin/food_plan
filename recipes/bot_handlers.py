import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from django.core.exceptions import ValidationError
from recipes.models import Customer, Recipe

logger = logging.getLogger(__name__)

(
    AWAIT_AGREEMENT,
    AWAIT_NAME,
    AWAIT_PHONE,
    AWAIT_MENU_CHOICE,
    AWAIT_RECIPE_ACTION,
    AWAIT_FAVORITES_ACTION,
    FINISH
) = range(7)


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
    with open('agreement.pdf', 'rb') as agreement_pdf_file:
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
        # context.bot.edit_message_reply_markup(
        #     chat_id=update.message.from_user.id,
        #     message_id=int(update.message.message_id) - 1,
        #     reply_markup=None
        # )
        update.message.reply_text(
            'Неверный формат телефона'
        )
        return request_contact(update, context)
    customer.save()
    update.message.reply_to_message.delete()
    return show_menu(update, context)


def show_menu(update, context):
    if update.callback_query:
        message = update.callback_query.message
    else:
        message = update.message
    keyboard = []
    keyboard.append([
        InlineKeyboardButton('🍴 Получить рецепт', callback_data='recipe'),
        InlineKeyboardButton('💖 Избранное', callback_data='favorites'),
    ])
    message.reply_text(
        'Уже голодны?',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return AWAIT_MENU_CHOICE


def show_recipe(update, context, after_dislike=False):
    query = update.callback_query
    query.message.delete()
    if after_dislike:
        context.bot.delete_message(query.from_user.id, int(query.message.message_id) - 1)
    customer = Customer.objects.get(telegramm_id=query.from_user.id)
    recipe = Recipe.objects.exclude(disliked_users=customer).order_by('?').first()
    if not recipe.image:
        image_filename = 'default.jpg'
    else:
        image_filename = recipe.image
    keyboard = []
    keyboard.append([
        InlineKeyboardButton('👍 Буду готовить!', callback_data=f'like-{recipe.id}'),
        InlineKeyboardButton('👎 Хочу другой рецепт', callback_data=f'dislike-{recipe.id}'),
    ])
    keyboard.append([
        InlineKeyboardButton('⬅️ В меню', callback_data='menu')
    ])
    with open(image_filename, 'rb') as image_file:
        query.message.reply_photo(
            image_file,
            caption=recipe.title
        )
    query.message.reply_text(
        f'{recipe.ingredients.strip()}\n\n{recipe.instruction.strip()}',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return AWAIT_RECIPE_ACTION


def handle_recipe_action(update, context):
    query = update.callback_query
    customer = Customer.objects.get(telegramm_id=query.from_user.id)
    if 'dislike' in query.data:
        recipe_id = int(query.data.replace('dislike-', ''))
        customer.dislikes.add(Recipe.objects.get(id=recipe_id))
        query.answer('Рецепт добавлен в чёрный список')
        return show_recipe(update, context, after_dislike=True)
    elif 'like' in query.data:
        recipe_id = int(query.data.replace('like-', ''))
        customer.likes.add(Recipe.objects.get(id=recipe_id))
        query.answer('Рецепт добавлен в избранное')
    return AWAIT_RECIPE_ACTION
    return AWAIT_MENU_CHOICE


def show_favorites(update, context):
    return AWAIT_FAVORITES_ACTION


def handle_favorites_action(update, context):
    return AWAIT_FAVORITES_ACTION
    return AWAIT_MENU_CHOICE
