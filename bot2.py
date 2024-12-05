from telethon import TelegramClient
from telethon.tl.types import ChannelParticipantsKicked

# Ваши данные для авторизации
api_id = 29733643
api_hash = 'fe6374e0aa4792328113106ac12a8bed'
session_name = 'my_session'  # Имя файла сессии

# Создание клиента
client = TelegramClient(session_name, api_id, api_hash)

async def get_banned_users(group_link):
    # Получаем объект группы по ссылке или юзернейму
    group = await client.get_entity(group_link)

    # Получаем список пользователей, забаненных в группе
    banned_users = await client.get_participants(
        group, 
        filter=ChannelParticipantsKicked()
    )

    return banned_users

async def main():
    group_link = input("Введите ссылку на группу или её юзернейм: ")
    banned_users = await get_banned_users(group_link)
    
    if banned_users:
        print("ID пользователей в черном списке:")
        for user in banned_users:
            print(f'ID: {user.id}, Имя: {user.first_name} {user.last_name or ""}')
    else:
        print("В черном списке группы нет пользователей.")

# Запуск клиента
with client:
    client.loop.run_until_complete(main())
