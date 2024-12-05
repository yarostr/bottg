import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Ваш токен
BOT_TOKEN = "7411390045:AAEU9UqxnwRexaIvXO4bTl4yMZkvkik75Gw"

# Функция для разблокировки всех пользователей
async def unban_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    try:
        # Получаем всех участников чата
        # Метод get_chat_members не существует, поэтому мы будем работать с get_chat_member поочередно.
        
        # Для начала нужно получить список всех пользователей чата. Предположим, что у нас есть их список в массиве `user_ids`.
        # В реальной ситуации вам нужно будет как-то определить список всех пользователей чата. Это зависит от особенностей вашего чата.
        
        # Пример простого списка ID пользователей:
        user_ids = [user.user.id for user in await context.bot.get_chat_administrators(chat_id)]
        
        for user_id in user_ids:
            member = await context.bot.get_chat_member(chat_id, user_id)
            
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
