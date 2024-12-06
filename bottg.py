import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Ваш токен
BOT_TOKEN = "7411390045:AAEU9UqxnwRexaIvXO4bTl4yMZkvkik75Gw"

# ID чата для уведомлений
NOTIFY_CHAT_ID = -1002226636763

# Файл с чаты для обработки
CHATS_FILE = "chats.txt"

# Файл с ID пользователей
USER_IDS_FILE = "user_ids.txt"

# Функция для отправки уведомлений
async def send_notification_to_admin(context: ContextTypes.DEFAULT_TYPE, message: str, chat_links: str, removed_count: int):
    try:
        # Отправляем уведомление в чат с ID NOTIFY_CHAT_ID
        await context.bot.send_message(
            NOTIFY_CHAT_ID,
            f"{message}\n\n"
            f"Чаты:\n{chat_links}\n"
            f"Количество удалённых пользователей: {removed_count}"
        )
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}")

# Функция для получения заблокированных пользователей
async def get_banned_users(context, chat_id):
    banned_users = []
    try:
        # Получаем список всех заблокированных пользователей
        async for member in context.bot.get_chat_administrators(chat_id):
            if member.status == "kicked":  # Проверяем, что пользователь заблокирован
                banned_users.append(member.user.id)
    except Exception as e:
        print(f"Ошибка при получении заблокированных пользователей: {e}")
    return banned_users

# Функция для извлечения ID из ссылки на чат
def extract_chat_id_from_link(chat_link: str):
    match = re.match(r"https://t.me/([a-zA-Z0-9_]+)", chat_link)
    if match:
        return match.group(1)  # Возвращаем username чата
    return None  # Если ссылка не подходит, возвращаем None

# Функция для обработки каждого чата из списка
async def process_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Чтение чатов из файла
        with open(CHATS_FILE, "r") as file:
            chats = file.readlines()

        # Формирование строки с ссылками на чаты
        chat_links = ""
        removed_count = 0

        for chat in chats:
            chat = chat.strip()  # Убираем лишние пробелы и символы новой строки
            if not chat:
                continue  # Пропускаем пустые строки

            # Если это ссылка на чат, извлекаем ID
            if chat.startswith("https://"):
                chat_id = extract_chat_id_from_link(chat)
                if not chat_id:
                    print(f"Невалидная ссылка на чат: {chat}")
                    continue
            else:
                # Если это ID чата, пытаемся преобразовать в целое число
                try:
                    chat_id = int(chat)
                except ValueError:
                    print(f"Невалидный ID чата: {chat}")
                    continue

            # Формируем ссылку на чат
            chat_links += f"https://t.me/{chat_id}\n"

            # Получаем список заблокированных пользователей
            banned_user_ids = await get_banned_users(context, chat_id)

            if not banned_user_ids:
                continue  # Если нет заблокированных пользователей, пропускаем этот чат

            # Записываем ID заблокированных пользователей в файл
            with open(USER_IDS_FILE, "a") as file:
                for user_id in banned_user_ids:
                    file.write(f"{user_id}\n")

            # Проходим по всем заблокированным пользователям и разблокируем их
            for user_id in banned_user_ids:
                try:
                    # Разблокируем пользователя
                    await context.bot.unban_chat_member(chat_id, user_id)
                    print(f"Пользователь с ID {user_id} был разблокирован.")
                    removed_count += 1  # Увеличиваем счётчик удалённых пользователей

                except Exception as e:
                    print(f"Не удалось разблокировать пользователя с ID {user_id}: {e}")

        # Отправляем уведомление об удалении
        await send_notification_to_admin(context, "Процесс удаления пользователей завершён.", chat_links, removed_count)

    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при обработке чатов: {str(e)}")

# Функция для обработки команды /unbanall
async def unban_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process_chats(update, context)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Добавляем обработчик для команды /unbanall
    app.add_handler(CommandHandler("unbanall", unban_all))

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
