import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Ваш токен
BOT_TOKEN = "7411390045:AAEU9UqxnwRexaIvXO4bTl4yMZkvkik75Gw"

async def unban_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    banned_users = await context.bot.get_chat_administrators(chat_id)

    for user in banned_users:
        if user.status == "kicked":
            await context.bot.unban_chat_member(chat_id, user.user.id)
    
    await update.message.reply_text("Все заблокированные пользователи были разблокированы.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("unbanall", unban_all))

    # Получаем публичный URL вашего проекта на Railway (например, bottg.up.railway.app)
    WEBHOOK_URL = "https://bottg.up.railway.app/bot" + BOT_TOKEN

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path=f"bot{BOT_TOKEN}",
        webhook_url=WEBHOOK_URL,
    )
