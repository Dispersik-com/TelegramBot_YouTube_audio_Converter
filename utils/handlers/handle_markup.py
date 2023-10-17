from telebot import types


def handle_markup(bot, chat_id: int, text: str, buttons: list[str]):
    """
    Handle and send a message with a custom keyboard markup.

    :param bot: The Telegram bot instance.
    :param chat_id: Chat ID of the recipient.
    :param text: Text content of the message.
    :param buttons: List of button labels for the custom keyboard.

    :return: None.
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for btn in buttons:
        markup.add(types.KeyboardButton(btn))
    bot.send_message(chat_id, text=text, reply_markup=markup)