import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Ваш токен
BOT_TOKEN = "7411390045:AAEU9UqxnwRexaIvXO4bTl4yMZkvkik75Gw"

# ID чата, в который нужно отправлять уведомления
NOTIFY_CHAT_ID = -1002226636763

# Путь к файлам с ID пользователей
USER_IDS_FILE = "user_ids.txt"
FAILED_UNBAN_FILE = "failed_unban_ids.txt"
REMOVED_FROM_CHAT_FILE = "removed_from_chat.txt"  # Новый файл для сохранения информации о удалённых пользователях

# GitHub token для пуша изменений (Ваш токен)
GITHUB_TOKEN = "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"

# Путь к вашему репозиторию на GitHub
GITHUB_REPO_URL = "https://github.com/your_username/your_repo.git"  # Замените на ваш репозиторий

# Флаг для остановки разблокировки
stop_ban = False

# Функция для отправки уведомлений в админ-чат
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

# Функция для отправки уведомления о начале удаления из чс
async def send_start_unban_notification(context: ContextTypes.DEFAULT_TYPE, chat_username: str):
    try:
        # Отправляем уведомление о начале процесса
        await context.bot.send_message(
            NOTIFY_CHAT_ID,
            f"Начинаю удаление пользователей из чёрного списка в чате @{chat_username}."
        )
    except Exception as e:
        print(f"Ошибка при отправке уведомления о начале удаления: {e}")

# Функция для пуша файла в репозиторию GitHub
def push_to_github():
    try:
        # Добавляем изменённый файл в git
        subprocess.run(["git", "add", FAILED_UNBAN_FILE, REMOVED_FROM_CHAT_FILE], check=True)

        # Создаём коммит
        subprocess.run(["git", "commit", "-m", "Update failed_unban_ids.txt and removed_from_chat.txt"], check=True)

        # Пушим изменения на GitHub с использованием токена
        subprocess.run(
            ["git", "push", f"https://{GITHUB_TOKEN}@{GITHUB_REPO_URL}"], check=True
        )

    except subprocess.CalledProcessError as e:
        print(f"Ошибка при пуше в репозиторий: {e}")

# Функция для обработки команды /unbanall
async def unban_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stop_ban  # Используем глобальный флаг
    chat_id = update.effective_chat.id
    try:
        # Проверяем, что команда /unbanall вызвана пользователем с ID 6093206594
        if update.effective_user.id != 6093206594:
            await update.message.reply_text("Эта команда доступна только для конкретного пользователя.")
            return

        # Получаем информацию о чате
        chat = await context.bot.get_chat(chat_id)
        chat_username = chat.username if chat.username else "Без имени"  # Если имя чата отсутствует, выводим "Без имени"

        # Отправляем уведомление о начале разблокировки в админ-чат
        await send_start_unban_notification(context, chat_username)

        # Чтение ID пользователей из файла
        with open(USER_IDS_FILE, "r") as file:
            blocked_user_ids = [line.strip() for line in file.readlines() if line.strip().isdigit()]
        
        removed_count = 0  # Счётчик удалённых пользователей
        failed_unban_ids = []  # Список для сохранения ID, которых не удалось разблокировать
        removed_from_chat = []  # Список для сохранения информации о пользователях и чатах, из которых их удалили

        # Проходим по всем заблокированным пользователям по ID
        for user_id in blocked_user_ids:
            if stop_ban:  # Если флаг для остановки разбана установлен, выходим из цикла
                await update.message.reply_text("Разблокировка остановлена.")
                break

            try:
                # Разблокируем пользователя
                await context.bot.unban_chat_member(chat_id, user_id)
                print(f"Пользователь с ID {user_id} был разблокирован в чате {chat_username}.")
                removed_count += 1  # Увеличиваем счётчик удалённых пользователей

                # Сохраняем информацию о пользователе и чате, из которого его удалили
                removed_from_chat.append(f"ID: {user_id}, Чат: @{chat_username}")

            except Exception as e:
                print(f"Не удалось разблокировать пользователя с ID {user_id}: {e}")
                failed_unban_ids.append(user_id)  # Добавляем ID в список неудачных разблокировок
        
        # Сохраняем список неудачных разблокировок в файл
        if failed_unban_ids:
            with open(FAILED_UNBAN_FILE, "a") as file:
                for user_id in failed_unban_ids:
                    file.write(f"{user_id}\n")
            print(f"Неудачные попытки разблокировки записаны в {FAILED_UNBAN_FILE}.")

        # Сохраняем информацию о пользователях, которых удалили, в файл
        if removed_from_chat:
            with open(REMOVED_FROM_CHAT_FILE, "a") as file:
                for entry in removed_from_chat:
                    file.write(f"{entry}\n")
            print(f"Информация о пользователях, которых удалили, записана в {REMOVED_FROM_CHAT_FILE}.")

        # Пушим изменения в репозиторий GitHub
        push_to_github()
        
        # Отправляем уведомление о завершении разблокировки в нужный чат
        await send_notification_to_admin(context, "Все заблокированные пользователи были разблокированы.", chat_username, removed_count)
    
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при попытке разблокировать пользователей: {str(e)}")

# Функция для обработки команды /stopban
async def stop_ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stop_ban
    stop_ban = True  # Устанавливаем флаг для остановки разблокировки
    await update.message.reply_text("Процесс разблокировки остановлен.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Добавляем обработчик для команды /unbanall
    app.add_handler(CommandHandler("unbanall", unban_all))

    # Добавляем обработчик для команды /stopban
    app.add_handler(CommandHandler("stopban", stop_ban_command))

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
