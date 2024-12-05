from telethon import TelegramClient
import os

api_id = 29733643
api_hash = 'fe6374e0aa4792328113106ac12a8bed'
session_name = 'my_session'

client = TelegramClient(session_name, api_id, api_hash)

async def main():
    phone = input("Введите номер телефона в формате +<7><9873000294>: ")

    # Попытка авторизации
    await client.start(phone=lambda: phone)

    # Если код подтверждения задан в переменной окружения, он будет автоматически использован
    code = os.getenv('TELEGRAM_CODE')
    if code:
        await client.sign_in(code=code)
        print("Авторизация завершена автоматически с использованием кода.")
    else:
        print("Не найден код подтверждения в переменных окружения. Пожалуйста, введите его вручную.")

    # Запрос информации о забаненных пользователях
    group_link = input("Введите ссылку на группу или её юзернейм: ")
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
