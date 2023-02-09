import asyncio
import os
import copy

from dataclasses import dataclass

from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message
from aiogram import Bot, Dispatcher, executor, types


API_TOKEN = '5879748147:AAGK8RabJ6wdzwI-PUKOcIwizjNa7E2SFBc'


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)



@dataclass
class Server:
    host: str
    owner_id: int
    status: bool


    
class Watcher:
    
    def __init__(self) -> None:
        self.servers = []
        
    
    def add_server(self, server: Server):
        self.servers.append(server)
    
        
    async def check_online(self, server: Server) -> bool:
        response = os.system("ping -c 1 -W 1 " + server.host)
        print(response)
        if response == 0:
            return True
        else:
            return False
    
    
    async def send_alert(self, server: Server):
        await bot.send_message(
            chat_id=server.owner_id,
            text=f"Сервер {server.host} теперь {'онлайн' if server.status else 'оффлайн'}"
        )        
        
    async def watch(self):
        while True:
            for server in self.servers:
                try:
                    status = await self.check_online(server)
                    if status == server.status:
                        continue
                    new_server = copy.deepcopy(server)
                    new_server.status = status
                    self.servers.remove(server)
                    self.servers.append(new_server)
                    await self.send_alert(new_server)
                except Exception as e:
                    print(e)
            await asyncio.sleep(1)
            
            
watcher = Watcher()              
       
       
@dp.message_handler(commands=['start'])
async def start(message: Message):
    await message.answer("Добро пожаловать в бота. \nВведите /add {адресс} для добавления роутера")


@dp.message_handler(commands=['add'])
async def add_ip(message: Message):
    args = message.get_args()
    if not args:
        await message.answer("Не верно введена команда")
        return
    server_host = args
    server = Server(server_host, message.from_id, True)
    is_online = await watcher.check_online(server)
    if is_online:
        watcher.add_server(server)
        await message.answer("Сервер добавлен в мониторинг")
        await message.answer(f"Сервер {server.host} теперь {'онлайн' if server.status else 'оффлайн'}")
    else:
        await message.answer("Сервер офлайн")
        
    
    

async def startup(dp):
    print("Бот запустился")
    asyncio.create_task(watcher.watch())
    
    
if __name__ == "__main__":
    executor.start_polling(dp, on_startup=startup)