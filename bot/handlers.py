import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

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


def start(update, context):
    keyboard = []
    keyboard.append([
        InlineKeyboardButton('✅ Принять', callback_data='agree'),
        InlineKeyboardButton('❌ Отклонить', callback_data='disagree'),
    ])
    with open('agreement.pdf', 'rb') as agreement_pdf_file:
        context.bot.send_document(
            update.message.from_user.id,
            agreement_pdf_file,
            caption='Вас приветствует FoodPlan! Продолжая работу, вы соглашаетесь с обработкой персональных данных.',
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
    query.message.reply_text(
        'Вы не согласились с политикой обработки персональных данных. Нажмите /start для повторного вызова.'
    )
    return FINISH


def handle_name(update, context):
    customer_name = update.message.text
    print(customer_name)
    # TODO: save customer name
    keyboard = [[KeyboardButton('☎ Передать контакт', request_contact=True)]]
    # update.message.delete()
    update.message.reply_text(
        'Укажите ваш телефон, нажав на кнопку «Передать контакт», или простым текстом',
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return AWAIT_PHONE


def handle_phone(update, context):
    if update.message.contact:
        phone_number = update.message.contact.phone_number
    else:
        phone_number = update.message.text
    print(phone_number)
    # TODO: save customer phone number
    keyboard = []
    keyboard.append([
        InlineKeyboardButton('🍽️ Получить рецепт', callback_data='recipe'),
        InlineKeyboardButton('💖 Избранное', callback_data='favorites'),
    ])
    update.message.reply_text(
        'Спасибо за регистрацию!',
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
