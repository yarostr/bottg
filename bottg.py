import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Ваш токен
BOT_TOKEN = "7411390045:AAEU9UqxnwRexaIvXO4bTl4yMZkvkik75Gw"

# Список ID пользователей, которых нужно разблокировать (например, сохраняйте их в базе данных)
blocked_user_ids = [292525734]  # Пример ID пользователей, которых заблокировали

# Функция для разблокировки всех пользователей по ID
async def unban_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    try:
        # Проходим по всем заблокированным пользователям по ID
        for user_id in blocked_user_ids:
            try:
                # Разблокируем пользователя, если его ID есть в списке
                await context.bot.unban_chat_member(chat_id, user_id)
                print(f"Пользователь с ID {user_id} был разблокирован.")
                
            except Exception as e:
                print(f"Не удалось разблокировать пользователя с ID {user_id}: {e}")
        
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
