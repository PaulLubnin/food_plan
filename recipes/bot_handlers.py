import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from recipes.models import Customer

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
    customer.save()
    # TODO: validate customer phone number
    update.message.reply_text(
        'Спасибо за регистрацию!',
        reply_markup=ReplyKeyboardMarkup([[]])
    )
    return show_menu(update, context)


def show_menu(update, context):
    keyboard = []
    keyboard.append([
        InlineKeyboardButton('🍽️ Получить рецепт', callback_data='recipe'),
        InlineKeyboardButton('💖 Избранное', callback_data='favorites'),
    ])
    update.message.reply_text(
        'Уже голодны?',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return AWAIT_MENU_CHOICE


def handle_menu_choice(update, context):
    return AWAIT_RECIPE_ACTION
    return AWAIT_FAVORITES_ACTION


def handle_recipe_action(update, context):
    return AWAIT_RECIPE_ACTION
    return AWAIT_MENU_CHOICE


def handle_favorites_action(update, context):
    return AWAIT_FAVORITES_ACTION
    return AWAIT_MENU_CHOICE
