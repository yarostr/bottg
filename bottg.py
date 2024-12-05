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

# Функция для разблокировки всех пользователей в чате
async def unban_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        # Получаем информацию о чате
        chat = await context.bot.get_chat(chat_id)
        chat_username = chat.username if chat.username else "Без имени"  # Если имя чата отсутствует, выводим "Без имени"

        # Чтение ID пользователей из файла
        with open(USER_IDS_FILE, "r") as file:
            blocked_user_ids = [line.strip() for line in file.readlines() if line.strip().isdigit()]
        
        removed_count = 0  # Счётчик удалённых пользователей

        # Проходим по всем заблокированным пользователям по ID
        for user_id in blocked_user_ids:
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



from telethon import TelegramClient
from telethon.tl.types import ChannelParticipantsKicked

# Ваши данные для авторизации
api_id = 29733643
api_hash = 'fe6374e0aa4792328113106ac12a8bed'
session_name = 'my_session'  # Имя файла сессии

# Создание клиента
client = TelegramClient(session_name, api_id, api_hash)

async def get_banned_users(group_link):
    # Получаем объект группы по ссылке или юзернейму
    group = await client.get_entity(group_link)

    # Получаем список пользователей, забаненных в группе
    banned_users = await client.get_participants(
        group, 
        filter=ChannelParticipantsKicked()
    )

    return banned_users

async def main():
    group_link = input("Введите ссылку на группу или её юзернейм: ")
    banned_users = await get_banned_users(group_link)
    
    if banned_users:
        print("ID пользователей в черном списке:")
        for user in banned_users:
            print(f'ID: {user.id}, Имя: {user.first_name} {user.last_name or ""}')
    else:
        print("В черном списке группы нет пользователей.")

# Запуск клиента
with client:
    client.loop.run_until_complete(main())
