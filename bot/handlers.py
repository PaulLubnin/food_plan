import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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
    return AWAIT_AGREEMENT


def handle_agreement(update, context):
    return AWAIT_NAME
    return FINISH


def handle_name(update, context):
    return AWAIT_PHONE


def handle_phone(update, context):
    return AWAIT_MENU_CHOICE,


def show_menu(update, context):
    return AWAIT_RECIPE_ACTION
    return AWAIT_FAVORITES_ACTION


def show_recipe(update, context):
    return AWAIT_RECIPE_ACTION
    return AWAIT_MENU_CHOICE


def show_favorites(update, context):
    return AWAIT_FAVORITES_ACTION
    return AWAIT_MENU_CHOICE
