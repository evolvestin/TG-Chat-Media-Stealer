import os
import random
import string
import objects
from objects import time_now, GoogleDrive
from telethon.sync import TelegramClient, events
# =================================================================================================================
stamp1 = time_now()
chats = eval(os.environ['chats'])
Auth = objects.AuthCentre(ID_DEV=os.environ['ID_DEV'], TOKEN=os.environ['DEV_TOKEN'])


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
                if response.message and response.message.media and \
                        all(key is None for key in [response.message.sticker, response.message.dice]):
                    try:
                        file_name = ''.join(random.sample(string.ascii_letters, 10))
                        path = await client.download_media(response.message.media, file_name)
                        if path:
                            await client.send_file(chats.get(chat_id), path,
                                                   caption=response.message.message,
                                                   formatting_entities=response.message.entities)
                            os.remove(path)
                    except IndexError and Exception:
                        Auth.dev.executive(None)
            Auth.dev.printer(f"Сессия в работе: {os.environ['session']}")
            client.run_until_disconnected()
    except IndexError and Exception:
        Auth.dev.thread_except()


if __name__ == '__main__' and os.environ.get('local'):
    start(stamp1)
