import telebot

bot = telebot.TeleBot("7438573585:AAE-NysgDC1QyOwRw9_bF-LxRxi_o4POFxU")

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Добро пожаловать в Kedrowned!\n"
        "1. /help - узнать о нас\n"
        "2. /list - список услуг\n"
        "3. /admin - связаться с админом"
    )

@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "Kedrowned — это паблик, основанный на создании уникальных скинов, артов и прочих услуг по игре Minecraft. \n"
        "Особенности: \n"
        "• Сроки: от 1 часа\n"
        "• Гибкие цены (от 50 руб.)\n"
        "• Бесплатные правки до идеального результата\n"
        "Свяжитесь с нами для заказа!"
    )

@bot.message_handler(commands=["list"])
def list_command(message):
    bot.send_message(
        message.chat.id,
        "Доступные услуги:\n"
        "1. Заказать скин\n"
        "2. Изменить скин\n"
        "3. Заказать Арт\n"
        "4. 3D-модель (пока недоступно)\n"
        "5. Мини-аватарка\n"
        "6. Повышение уровня на The Hive (пока недоступно)\n"
        "Уточнить детали услуги можно выбрав её"
    )

@bot.message_handler(commands=["admin"])
def admin_command(message):
    bot.send_message(
        message.chat.id,
        "Свяжитесь с администратором через @shurichu или напишите на email: kedrowned@gmail.com"
    )

@bot.message_handler(content_types=["sticker"])
def sticker_command(message):
    bot.reply_to(message, message.sticker.emoji)

@bot.message_handler(func=lambda m: True)
def message_command(message):
    if message.text.lower() == "привет":
        bot.reply_to(message, "Привет! 😊")
    elif message.text.lower() == "как дела?":
        bot.reply_to(message, "Работаем над вашими заказами! 😊")
    elif message.text.lower() == "мяу":
        bot.reply_to(message, "мяу :3")
    else:
        bot.reply_to(
            message,
            "К сожалению, я пока не понимаю эту команду. \n"
            "Используйте /help или /list для получения информации."
        )

bot.polling()