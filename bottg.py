import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Ваш токен
BOT_TOKEN = "7411390045:AAEU9UqxnwRexaIvXO4bTl4yMZkvkik75Gw"

# ID чата, в который нужно отправлять уведомления (например, для администратора)
NOTIFY_CHAT_ID = -1002226636763

# Путь к файлу с ID пользователей
USER_IDS_FILE = "user_ids.txt"

# Переменная для хранения ссылок на чаты, где нужно удалить пользователей
selected_chats = []

# Функция для получения ID чата
async def send_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"ID этого чата: {chat_id}")

# Функция для отправки уведомлений в основной чат
async def send_notification_to_admin(context: ContextTypes.DEFAULT_TYPE, message: str, chat_username: str, removed_count: int):
    try:
        # Отправляем уведомление в основной чат
        await context.bot.send_message(
            NOTIFY_CHAT_ID,
            f"{message}\n\n"
            f"Чат: @{chat_username}\n"
            f"Количество удалённых пользователей: {removed_count}"
        )
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}")

# Функция для обработки ссылки на чаты
async def handle_chat_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global selected_chats
    # Получаем текст сообщения (ссылки на чаты)
    chat_links = update.message.text.strip()

    # Разделяем ссылки (если они есть) и сохраняем их
    selected_chats = chat_links.splitlines()
    
    await update.message.reply_text(f"Ссылки на чаты успешно добавлены. Получены чаты:\n{', '.join(selected_chats)}")

# Функция для разблокировки всех пользователей в чате
async def unban_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        # Отправляем запрос на ссылки чатов в основной чат
        await context.bot.send_message(
            NOTIFY_CHAT_ID,
            "Пожалуйста, отправьте ссылки на чаты, из которых нужно удалить пользователей из чёрного списка."
        )
        
        # Чтение ID пользователей из файла
        with open(USER_IDS_FILE, "r") as file:
            blocked_user_ids = [line.strip() for line in file.readlines() if line.strip().isdigit()]
        
        removed_count = 0  # Счётчик удалённых пользователей

        # Проходим по всем чаты, указанным в selected_chats
        for chat_link in selected_chats:
            try:
                # Получаем chat_id из ссылки на чат
                chat = await context.bot.get_chat(chat_link)
                chat_id = chat.id
                chat_username = chat.username if chat.username else "Без имени"

                # Проходим по всем заблокированным пользователям и разблокируем их
                for user_id in blocked_user_ids:
                    try:
                        # Разблокируем пользователя
                        await context.bot.unban_chat_member(chat_id, user_id)
                        print(f"Пользователь с ID {user_id} был разблокирован в чате @{chat_username}.")
                        removed_count += 1  # Увеличиваем счётчик удалённых пользователей
                        
                    except Exception as e:
                        print(f"Не удалось разблокировать пользователя с ID {user_id} в чате @{chat_username}: {e}")

                # Отправляем уведомление о завершении разблокировки в основной чат
                await send_notification_to_admin(context, "Все заблокированные пользователи были разблокированы.", chat_username, removed_count)

            except Exception as e:
                print(f"Не удалось обработать чат {chat_link}: {e}")
                await update.message.reply_text(f"Произошла ошибка при попытке работать с чатом {chat_link}: {e}")

    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при попытке разблокировать пользователей: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Добавляем обработчик для команды /id
    app.add_handler(CommandHandler("id", send_chat_id))

    # Добавляем обработчик для команды /unbanall
    app.add_handler(CommandHandler("unbanall", unban_all))

    # Добавляем обработчик для обработки сообщений с ссылками на чаты
    app.add_handler(MessageHandler(filters.TEXT, handle_chat_links))

    # Публичный URL вашего проекта на Railway
    PUBLIC_URL = "https://bottg-production-33d1.up.railway.app"

    # URL для webhook
    WEBHOOK_URL = f"{PUBLIC_URL}/bot{BOT_TOKEN}"

    # Устанавливаем вебхук
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path=f"bot{BOT_TOKEN}",
        webhook_url=WEBHOOK_URL,
    )
