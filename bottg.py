import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Ваш токен
BOT_TOKEN = "7411390045:AAEU9UqxnwRexaIvXO4bTl4yMZkvkik75Gw"

# ID чата, в который нужно отправлять уведомления
NOTIFY_CHAT_ID = -1002226636763

# Файл с ID пользователей для разблокировки
USER_IDS_FILE = "user_ids.txt"

# Список разрешённых пользователей
ALLOWED_USERS = [6093206594, 1786923925]  # Добавьте сюда ID пользователей, которым разрешено использовать команду

# Флаг для остановки процесса разблокировки
stop_ban = False

# Функция для получения ID чата
async def send_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"ID этого чата: {chat_id}")

# Функция для отправки уведомлений о начале процесса разблокировки
async def send_start_unban_notification(context: ContextTypes.DEFAULT_TYPE, chat_username: str):
    try:
        await context.bot.send_message(
            NOTIFY_CHAT_ID,
            f"Начато удаление пользователей из черного списка в чате @{chat_username}."
        )
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}")

# Функция для отправки уведомлений о завершении процесса
async def send_notification_to_admin(context: ContextTypes.DEFAULT_TYPE, message: str, chat_username: str, removed_count: int):
    try:
        await context.bot.send_message(
            NOTIFY_CHAT_ID,
            f"{message}\n\n"
            f"Чат: @{chat_username}\n"
            f"Количество удалённых пользователей: {removed_count}"
        )
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}")

# Функция для разблокировки всех пользователей в чате
async def unban_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stop_ban
    chat_id = update.effective_chat.id

    # Проверяем, что пользователь имеет разрешение
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("У вас нет разрешения на выполнение этой команды.")
        return

    try:
        # Получаем информацию о чате
        chat = await context.bot.get_chat(chat_id)
        chat_username = chat.username if chat.username else "Без имени"

        # Уведомляем о начале процесса
        await send_start_unban_notification(context, chat_username)

        # Читаем ID пользователей из файла
        with open(USER_IDS_FILE, "r") as file:
            blocked_user_ids = [line.strip() for line in file.readlines() if line.strip().isdigit()]
        
        removed_count = 0
        failed_unban_ids = []
        removed_from_chat = []

        # Разблокировка пользователей
        for user_id in blocked_user_ids:
            if stop_ban:
                await update.message.reply_text("Разблокировка остановлена.")
                break

            try:
                await context.bot.unban_chat_member(chat_id, user_id)
                print(f"Пользователь с ID {user_id} был разблокирован в чате {chat_username}.")
                removed_count += 1
                removed_from_chat.append(f"ID: {user_id}, Чат: @{chat_username}")
            except Exception as e:
                print(f"Не удалось разблокировать пользователя с ID {user_id}: {e}")
                failed_unban_ids.append(user_id)

        # Отправляем уведомление об окончании
        await send_notification_to_admin(context, "Разблокировка завершена.", chat_username, removed_count)

    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")

# Команда для остановки разблокировки
async def stop_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stop_ban

    # Проверяем разрешение пользователя
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("У вас нет разрешения на выполнение этой команды.")
        return

    stop_ban = True
    await update.message.reply_text("Процесс разблокировки остановлен.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Обработчики команд
    app.add_handler(CommandHandler("id", send_chat_id))
    app.add_handler(CommandHandler("unbanall", unban_all))
    app.add_handler(CommandHandler("stopban", stop_unban))

    # URL для webhook
    PUBLIC_URL = "https://bottg-production-33d1.up.railway.app"
    WEBHOOK_URL = f"{PUBLIC_URL}/bot{BOT_TOKEN}"

    # Устанавливаем вебхук
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path=f"bot{BOT_TOKEN}",
        webhook_url=WEBHOOK_URL,
    )
