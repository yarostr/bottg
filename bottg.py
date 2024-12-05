import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Ваш токен
BOT_TOKEN = "7411390045:AAEU9UqxnwRexaIvXO4bTl4yMZkvkik75Gw"

async def unban_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    try:
        # Получаем количество участников чата
        members_count = await context.bot.get_chat_members_count(chat_id)

        # Проходим по всем участникам
        for i in range(members_count):
            member = await context.bot.get_chat_member(chat_id, i)

            # Проверяем, заблокирован ли пользователь
            if member.status == 'kicked':  # 'kicked' означает, что пользователь заблокирован
                await context.bot.unban_chat_member(chat_id, member.user.id)

        await update.message.reply_text("Все заблокированные пользователи были разблокированы.")
    
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при попытке разблокировать пользователей: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
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
