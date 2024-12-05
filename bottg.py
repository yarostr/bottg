from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

# Ваш токен, который вы получили от @BotFather
BOT_TOKEN = "7411390045:AAEU9UqxnwRexaIvXO4bTl4yMZkvkik75Gw"

async def unban_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Получаем список заблокированных пользователей
    banned_users = await context.bot.get_chat_administrators(chat_id)
    
    for user in banned_users:
        if user.status == "kicked":  # Проверяем, что пользователь заблокирован
            await context.bot.unban_chat_member(chat_id, user.user.id)
    
    await update.message.reply_text("Все заблокированные пользователи были разблокированы.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Команда /unbanall разблокирует всех
    app.add_handler(CommandHandler("unbanall", unban_all))

    print("Бот запущен...")
    app.run_polling()
