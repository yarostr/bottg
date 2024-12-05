import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Получаем токен из переменной окружения
BOT_TOKEN = os.environ.get("7411390045:AAEU9UqxnwRexaIvXO4bTl4yMZkvkik75Gw")

async def unban_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Получаем информацию о заблокированных пользователях по диапазону user_id
    user_id_range = range(0, 10000000)  # Можно уточнить диапазон

    unbanned_count = 0
    for user_id in user_id_range:
        try:
            await context.bot.unban_chat_member(chat_id, user_id)
            unbanned_count += 1
        except Exception:
            pass  # Игнорируем ошибки, если пользователь не забанен или не существует
    
    await update.message.reply_text(f"Разблокировано {unbanned_count} пользователей.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Добавляем обработчик команды /unbanall
    app.add_handler(CommandHandler("unbanall", unban_all))

    print("Бот запущен...")
    app.run_polling()
