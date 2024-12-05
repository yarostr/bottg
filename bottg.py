from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Ваш токен бота
BOT_TOKEN = "7411390045:AAEU9UqxnwRexaIvXO4bTl4yMZkvkik75Gw"

async def unban_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    unbanned_count = 0

    # Попытка разблокировать всех пользователей по диапазону ID
    for user_id in range(1, 100000):  # Диапазон можно регулировать
        try:
            await context.bot.unban_chat_member(chat_id, user_id)
            unbanned_count += 1
        except Exception:
            pass  # Игнорируем ошибки для пользователей, которых нельзя разблокировать

    await update.message.reply_text(f"Разблокировано {unbanned_count} пользователей.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Обработка команды /unbanall
    app.add_handler(CommandHandler("unbanall", unban_all))

    print("Бот запущен...")
    app.run_polling()
