import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Ваш токен
BOT_TOKEN = "7411390045:AAEU9UqxnwRexaIvXO4bTl4yMZkvkik75Gw"

# ID чата, в который нужно отправлять уведомления (например, для администратора)
NOTIFY_CHAT_ID = -1002226636763

# Путь к файлу с ID пользователей
USER_IDS_FILE = "user_ids.txt"

# Функция для получения ID чата
async def send_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"ID этого чата: {chat_id}")

# Функция для отправки уведомлений в конкретный чат
async def send_notification_to_admin(context: ContextTypes.DEFAULT_TYPE, message: str, chat_username: str, removed_count: int):
    try:
        # Отправляем уведомление в чат с ID NOTIFY_CHAT_ID
        await context.bot.send_message(
            NOTIFY_CHAT_ID,
            f"{message}\n\n"
            f"Чат: @{chat_username}\n"
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

# Функция для разблокировки всех пользователей в чате
async def unban_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        # Получаем информацию о чате
        chat = await context.bot.get_chat(chat_id)
        chat_username = chat.username if chat.username else "Без имени"  # Если имя чата отсутствует, выводим "Без имени"

        # Получаем список заблокированных пользователей
        banned_user_ids = await get_banned_users(context, chat_id)
        
        if not banned_user_ids:
            await update.message.reply_text("Нет заблокированных пользователей в чате.")
            return
        
        # Записываем ID заблокированных пользователей в файл
        with open(USER_IDS_FILE, "a") as file:
            for user_id in banned_user_ids:
                file.write(f"{user_id}\n")
        
        removed_count = 0  # Счётчик удалённых пользователей

        # Проходим по всем заблокированным пользователям и разблокируем их
        for user_id in banned_user_ids:
            try:
                # Разблокируем пользователя
                await context.bot.unban_chat_member(chat_id, user_id)
                print(f"Пользователь с ID {user_id} был разблокирован.")
                removed_count += 1  # Увеличиваем счётчик удалённых пользователей
                
            except Exception as e:
                print(f"Не удалось разблокировать пользователя с ID {user_id}: {e}")
        
        # Отправляем уведомление о завершении разблокировки в нужный чат
        await send_notification_to_admin(context, "Все заблокированные пользователи были разблокированы.", chat_username, removed_count)
    
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при попытке разблокировать пользователей: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Добавляем обработчик для команды /id
    app.add_handler(CommandHandler("id", send_chat_id))
    
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
