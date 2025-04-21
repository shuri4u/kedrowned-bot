import logging
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = '804293894AAGc7nGPicU6DC4vHoABqvbmufn4tgLWX1M7:'

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

POPULAR_CRYPTO = {
    'bitcoin': 'Bitcoin (BTC)',
    'ethereum': 'Ethereum (ETH)',
    'binancecoin': 'Binance Coin (BNB)',
    'solana': 'Solana (SOL)',
    'ripple': 'XRP',
    'cardano': 'Cardano (ADA)',
    'dogecoin': 'Dogecoin (DOGE)',
    'polkadot': 'Polkadot (DOT)',
    'tether': 'Tether (USDT)'
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}!\n"
        "Я бот для отслеживания курсов криптовалют.\n"
        "Используй меню ниже для навигации:",
        reply_markup=main_menu_keyboard()
    )


def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 Популярные криптовалюты", callback_data='popular')],
        [InlineKeyboardButton("🔍 Поиск по названию", callback_data='search')],
        [InlineKeyboardButton("🏆 Топ-10 по капитализации", callback_data='top10')],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data='help')]
    ]
    return InlineKeyboardMarkup(keyboard)


async def get_crypto_data(crypto_id: str):
    try:
        response = requests.get(
            f"{COINGECKO_API_URL}/coins/{crypto_id}",
            params={
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'false',
                'developer_data': 'false',
                'sparkline': 'false'
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка получения данных для {crypto_id}: {e}")
        return None


async def show_crypto_price(update: Update, context: ContextTypes.DEFAULT_TYPE, crypto_id: str,
                            is_callback: bool = True):
    try:
        crypto_data = await get_crypto_data(crypto_id)
        if not crypto_data:
            raise ValueError("Не удалось получить данные")

        market_data = crypto_data.get('market_data', {})
        current_price = market_data.get('current_price', {}).get('usd', 0)
        price_change = market_data.get('price_change_percentage_24h', 0)

        message = (
            f"<b>{crypto_data.get('name', 'N/A')} ({crypto_data.get('symbol', '').upper()})</b>\n\n"
            f"💰 <b>Цена:</b> ${current_price:,.2f}\n"
            f"📈 <b>Изменение (24ч):</b> {price_change:+.2f}%\n\n"
            f"📊 <b>Капитализация:</b> ${market_data.get('market_cap', {}).get('usd', 0):,.0f}\n"
            f"🔄 <b>Объем (24ч):</b> ${market_data.get('total_volume', {}).get('usd', 0):,.0f}\n\n"
            f"🕒 <b>Обновлено:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Назад к списку", callback_data='popular')],
            [InlineKeyboardButton("🏠 Главное меню", callback_data='back_to_main')]
        ])

        if is_callback:
            await update.callback_query.edit_message_text(
                text=message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                text=message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )

    except Exception as e:
        logger.error(f"Ошибка отображения цены: {e}")
        error_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Назад", callback_data='popular')],
            [InlineKeyboardButton("🏠 Главное меню", callback_data='back_to_main')]
        ])

        if is_callback:
            await update.callback_query.edit_message_text(
                text="⚠️ Ошибка при получении данных. Попробуйте позже.",
                reply_markup=error_markup
            )
        else:
            await update.message.reply_text(
                text="⚠️ Ошибка при получении данных. Попробуйте позже.",
                reply_markup=error_markup
            )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    try:
        if query.data == 'popular':
            await show_crypto_menu(query)
        elif query.data == 'search':
            await start_search(query, context)
        elif query.data == 'top10':
            await show_top10(query)
        elif query.data == 'help':
            await show_help(query)
        elif query.data == 'back_to_main':
            await return_to_main_menu(query)
        elif query.data.startswith('price_'):
            crypto_id = query.data[6:]
            await show_crypto_price(update, context, crypto_id)
    except Exception as e:
        logger.error(f"Ошибка обработки кнопки: {e}")
        await handle_button_error(query)


async def show_crypto_menu(query):
    keyboard = []
    for crypto_id, crypto_name in POPULAR_CRYPTO.items():
        keyboard.append([InlineKeyboardButton(crypto_name, callback_data=f'price_{crypto_id}')])

    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data='back_to_main')])

    await query.edit_message_text(
        text="📊 Выберите криптовалюту:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def start_search(query, context):
    await query.edit_message_text(
        text="🔍 Введите название или тикер криптовалюты (например: bitcoin или btc):"
    )
    context.user_data['waiting_for_search'] = True


async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    search_query = update.message.text.lower().strip()
    context.user_data['waiting_for_search'] = False

    try:
        for crypto_id, crypto_name in POPULAR_CRYPTO.items():
            if search_query in crypto_id.lower() or search_query in crypto_name.lower():
                await show_crypto_price(update, context, crypto_id, False)
                return

        # Если не найдено в популярных, ищем через API
        response = requests.get(f"{COINGECKO_API_URL}/coins/list")
        response.raise_for_status()

        matches = [
            coin for coin in response.json()
            if search_query in coin['name'].lower() or search_query == coin['symbol'].lower()
        ]

        if not matches:
            await update.message.reply_text(
                "❌ Криптовалюта не найдена. Попробуйте другое название.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔍 Попробовать снова", callback_data='search')],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data='back_to_main')]
                ])
            )
        elif len(matches) == 1:
            await show_crypto_price(update, context, matches[0]['id'], False)
        else:
            keyboard = [
                [InlineKeyboardButton(
                    f"{coin['name']} ({coin['symbol'].upper()})",
                    callback_data=f'price_{coin["id"]}'
                )] for coin in matches[:5]  # Ограничиваем 5 результатами
            ]
            keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data='back_to_main')])

            await update.message.reply_text(
                "🔍 Найдено несколько вариантов:",
                reply_markup=InlineKeyboardMarkup(keyboard))

    except Exception as e:
        logger.error(f"Ошибка поиска: {e}")
        await update.message.reply_text(
            "⚠️ Ошибка при поиске. Попробуйте позже.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 Попробовать снова", callback_data='search')],
                [InlineKeyboardButton("🏠 Главное меню", callback_data='back_to_main')]
            ])
        )


async def show_top10(query):
    try:
        response = requests.get(
            f"{COINGECKO_API_URL}/coins/markets",
            params={
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 10,
                'page': 1,
                'sparkline': 'false'
            }
        )
        response.raise_for_status()

        message = "🏆 <b>Топ-10 криптовалют по капитализации</b>\n\n"
        for i, coin in enumerate(response.json(), 1):
            message += (
                f"{i}. <b>{coin['name']} ({coin['symbol'].upper()})</b>\n"
                f"💰 Цена: ${coin['current_price']:,.2f}\n"
                f"📈 Изменение 24ч: {coin['price_change_percentage_24h']:+.2f}%\n"
                f"💵 Капитализация: ${coin['market_cap']:,.0f}\n\n"
            )

        await query.edit_message_text(
            text=message,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ Назад", callback_data='back_to_main')]
            ])
        )
    except Exception as e:
        logger.error(f"Ошибка получения топа: {e}")
        await query.edit_message_text(
            text="⚠️ Ошибка при получении топа. Попробуйте позже.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Попробовать снова", callback_data='top10')],
                [InlineKeyboardButton("🏠 Главное меню", callback_data='back_to_main')]
            ])
        )


async def show_help(query):
    await query.edit_message_text(
        text="ℹ️ <b>Справка по боту</b>\n\n"
             "Этот бот показывает актуальные курсы криптовалют с использованием данных CoinGecko API.\n\n"
             "<b>Основные команды:</b>\n"
             "/start - показать главное меню\n"
             "/help - показать эту справку\n"
             "/price [название] - узнать цену криптовалюты\n\n"
             "<b>Как использовать:</b>\n"
             "1. Выберите криптовалюту из списка\n"
             "2. Или введите её название для поиска\n"
             "3. Просматривайте актуальные данные о ценах",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Главное меню", callback_data='back_to_main')]
        ])
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text="ℹ️ <b>Справка по боту</b>\n\n"
             "Этот бот показывает актуальные курсы криптовалют с использованием данных CoinGecko API.\n\n"
             "<b>Основные команды:</b>\n"
             "/start - показать главное меню\n"
             "/help - показать эту справку\n"
             "/price [название] - узнать цену криптовалюты\n\n"
             "Используйте кнопки меню для навигации.",
        parse_mode='HTML',
        reply_markup=main_menu_keyboard()
    )


async def return_to_main_menu(query):
    await query.edit_message_text(
        text="Главное меню:",
        reply_markup=main_menu_keyboard()
    )


async def handle_button_error(query):
    await query.edit_message_text(
        text="⚠️ Произошла ошибка. Пожалуйста, попробуйте позже.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Главное меню", callback_data='back_to_main')]
        ])
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_search', False):
        await handle_search(update, context)
    else:
        await update.message.reply_text(
            "Используйте меню для навигации или команду /help для справки.",
            reply_markup=main_menu_keyboard()
        )


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Используйте: /price <название_криптовалюты>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 Начать поиск", callback_data='search')]
            ])
        )
        return

    search_query = ' '.join(context.args).lower()
    context.user_data['search_query'] = search_query
    await handle_search(update, context)


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("price", price_command))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()