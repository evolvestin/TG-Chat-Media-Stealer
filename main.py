import os
import random
import string
import asyncio
import objects
import _thread
from time import sleep
from telethon.sync import TelegramClient, events
from objects import time_now, AuthCentre, GoogleDrive
# =====================================================================================================================


def client_init(auth: AuthCentre, chats: dict):
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
        auth.dev.printer(f"Инициализация {os.environ['session']}")
        client = TelegramClient(os.environ['session'], int(os.environ['api_id']), os.environ['api_hash']).start()
        with client:
            @client.on(events.NewMessage(chats=list(chats.keys())))
            async def response_user_update(response):
                chat_id = response.message.peer_id.channel_id
                chat_id = chat_id if '-100' in str(chat_id) else int(f'-100{chat_id}')
                if response.message and response.message.media and \
                        all(key is None for key in [response.message.sticker, response.message.dice]):
                    path, file_name = None, ''.join(random.sample(string.ascii_letters, 10))

                    try:
                        path = await client.download_media(response.message.media, file_name)
                    except IndexError and Exception:
                        auth.dev.executive(None)

                    if path:
                        try:
                            caption = response.message.message[:1024] if response.message.message else None

                            await client.send_file(chats.get(chat_id), path, caption=caption,
                                                   formatting_entities=response.message.entities, nosound_video=False)
                        except IndexError and Exception as error:
                            if 'The caption is too long' not in str(error):
                                auth.dev.executive(None)
                        try:
                            os.remove(path)
                        except IndexError and Exception:
                            auth.dev.executive(None)
            auth.dev.printer(f"Сессия в работе: {os.environ['session']}")
            client.run_until_disconnected()
    except IndexError and Exception:
        try:
            auth.dev.thread_except()
        except IndexError and Exception as error:
            auth.dev.printer(f'Не удалось отправить ошибку ({error}). Стартуем заново client_init()')
        _thread.start_new_thread(client_init, (auth, chats))


def start(stamp: int = time_now()):
    objects.environmental_files()
    chats: dict = eval(os.environ['chats'])
    drive_client = GoogleDrive('google.json')
    auth = objects.AuthCentre(ID_DEV=os.environ['ID_DEV'], TOKEN=os.environ['DEV_TOKEN'])

    for file in drive_client.files():
        user_session = f"{os.environ['session']}.session"
        if file['name'] == user_session:
            drive_client.download_file(file['id'], f'{user_session}')
            auth.dev.printer(f'Скачали сессию Telegram: {user_session}')

    if os.environ.get('local'):
        auth.dev.printer(f'Запуск скрипта локально за {time_now() - stamp} сек.')
    else:
        auth.dev.start(stamp)
        auth.dev.printer(f'Скрипт запущен за {time_now() - stamp} сек.')

    _thread.start_new_thread(client_init, (auth, chats))
    while True:
        sleep(24 * 60 * 60)


if __name__ == '__main__':
    start()
