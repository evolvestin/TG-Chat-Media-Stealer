import os
import objects
from objects import time_now, GoogleDrive
from telethon.sync import TelegramClient, events
# =================================================================================================================
stamp1 = time_now()
Auth, chats = objects.AuthCentre(ID_DEV=os.environ['ID_DEV'], TOKEN=os.environ['DEV_TOKEN']), eval(os.environ['chat'])


def sessions_creation():
    objects.environmental_files()
    drive_client = GoogleDrive('google.json')
    for file in drive_client.files():
        user_session = f"{os.environ['session']}.session"
        if file['name'] == user_session:
            drive_client.download_file(file['id'], f'{user_session}')
            Auth.dev.printer(f'Скачали сессию Telegram: {user_session}')


sessions_creation()
# =================================================================================================================


def start(stamp):
    try:
        if os.environ.get('local'):
            Auth.dev.printer(f'Запуск скрипта локально за {time_now() - stamp} сек.')
        else:
            Auth.dev.start(stamp1)
            Auth.dev.printer(f'Скрипт запущен за {time_now() - stamp} сек.')
        client = TelegramClient(os.environ['session'], int(os.environ['api_id']), os.environ['api_hash']).start()
        with client:
            @client.on(events.NewMessage(chats=list(chats.keys())))
            async def response_user_update(response):
                chat_id = response.message.peer_id.channel_id
                chat_id = chat_id if '-100' in str(chat_id) else int(f'-100{chat_id}')
                if response.message and response.message.media:
                    await client.send_message(chats.get(chat_id), response.message)
            Auth.dev.printer(f"Сессия в работе: {os.environ['session']}")
            client.run_until_disconnected()
    except IndexError and Exception:
        Auth.dev.thread_except()


if __name__ == '__main__' and os.environ.get('local'):
    start(stamp1)
