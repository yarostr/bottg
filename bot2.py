from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import os

# Ваши данные для авторизации
api_id = 29733643
api_hash = 'fe6374e0aa4792328113106ac12a8bed'
session_name = 'my_session'

# Номер телефона, который вы хотите использовать для авторизации
phone = '+79123456789'  # Укажите свой номер телефона явно

client = TelegramClient(session_name, api_id, api_hash)

async def main():
    try:
        # Попытка авторизации
        await client.start(phone=phone)
        print("Авторизация успешна!")

    except SessionPasswordNeededError:
        # В случае двухфакторной авторизации
        password = input("Введите двухфакторный пароль: ")
        await client.start(phone=phone, password=password)
        print("Авторизация успешна!")

    # Запрос информации о группе
    group_link = input("Введите ссылку на группу или её юзернейм: ")

    # Пример функции для получения пользователей в ЧС
    banned_users = await get_banned_users(group_link)
    
    if banned_users:
        print("ID пользователей в черном списке:")
        for user in banned_users:
            print(f'ID: {user.id}, Имя: {user.first_name or ""} {user.last_name or ""}')
    else:
        print("В черном списке группы нет пользователей.")

# Запуск клиента
with client:
    client.loop.run_until_complete(main())
