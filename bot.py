from aiologger import Logger

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

import re
import redis
import ctypes
import glob

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

from candle import get_data
from db import create_table, save_to_db

# TODO: add aiogram_dialog
# from aiogram_dialog import Dialog, DialogManager, DialogRegistry, Window, StartMode
# from aiogram_dialog.widgets.kbd import SwitchTo, Button, Column


# Configure bot token
API_TOKEN = '5943100350:AAFc_QxpURpcZSsiFsRlGBd3dMCOAz1uMwE'

# Configure Candle URL
URL = 'https://candle.fmph.uniba.sk/'

# Path to chromedriver
PATH = r'/opt/WebDriver/bin/chromedriver'

# Initialize libfile to use C++ DB functions
libfile = glob.glob('build/lib*/*.so')[0]
lib = ctypes.CDLL(libfile)

lib.createTable.restype = ctypes.c_void_p
lib.saveToDB.restype = ctypes.c_void_p

lib.saveToDB.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
lib.createTable.argtypes = [ctypes.c_void_p]


# Initialize webdriver options
service = Service(PATH)
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('disable-infobars')
options.add_argument('--disable-extensions')
options.add_argument('start-maximized')

DRIVER = webdriver.Chrome(service=service, options=options)

# Configure logging
logger = Logger.with_default_handlers(name='my-logger')

# Initialize redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Create table in the database if it doesn't exist
lib.createTable(None)


# Check if redis is connected
try:
    r.ping()
    print('[OK] Redis connected')
except redis.exceptions.ConnectionError:
    print('[ERROR] Redis not connected')

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)

# Initialize storage to save user state
storage = MemoryStorage()

# Initialize dispatcher
dp = Dispatcher(bot, storage=storage)


# Create state machine with the states
class Menu(StatesGroup):
    start = State()
    schedule = State()
    group = State()
    teacher = State()
    audience = State()
    

class StartMenu:
    """Create the first menu with three buttons 'Schedule', 'About', 'Help'"""

    def __init__(self):
        self.keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        self.keyboard.row('📚 Расписание', '📝 Помощь', '📚 О боте')

    def get_keyboard(self):
        return self.keyboard


class ScheduleMenu:
    """Create the second menu with three buttons 'Group', 'Teacher', 'Audience', 'Back'"""
    def __init__(self):
        self.keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        self.keyboard.row('📚 Группа', '📚 Препод', '📚 Аудитория', '🔙 Назад')

    def get_keyboard(self):
        return self.keyboard


# Create handlers to process the first menu
@dp.message_handler(commands='start')
async def process_start_command(message: types.Message):
    # Create table in the database if it doesn't exist

    logger.info('User {} started the bot'.format(message.from_user.id))

    # Set state to the first menu
    await Menu.start.set()
    await message.reply('Привет, я бот для расписания UK. Что тебе нужно?', reply_markup=StartMenu().get_keyboard())
    

# Create handler to process the second menu
@dp.message_handler(state=Menu.start)
async def process_second_menu(message: types.Message, state: FSMContext):
    logger.info('User {} chose the option {}'.format(message.from_user.id, message.text))

    if message.text == '📚 Расписание':
        await Menu.schedule.set()
        await message.reply('Выбери тип расписания', reply_markup=ScheduleMenu().get_keyboard())

    elif message.text == '📝 Помощь':
        await message.reply('Я бот для расписания UK. Я могу показать тебе расписание группы, преподавателя или аудитории. '
                            'Для этого нажми на кнопку "📚 Расписание" и выбери нужный тип расписания. '
                            'После этого введи название группы, преподавателя или аудитории. '
                            'Если тебе нужно вернуться в главное меню, нажми на кнопку "🔙 Назад"')

    elif message.text == '📚 О боте':
        await message.reply('Сделано с ❤ @kayfolom2009 для наших русскоязычных друзей и подруг. Бот находится в стадии разработки, если вы заметили какие-то ошибки, пожалуйста, напишите мне в личные сообщения.')


# Create handler for the second menu
@dp.message_handler(state=Menu.schedule)
async def process_third_menu(message: types.Message, state: FSMContext):
    logger.info('User {} chose the option {}'.format(message.from_user.id, message.text))

    if message.text == '📚 Группа':
        await Menu.group.set()
        await message.reply('Введите название группы (например, 1inf1, 1INF1)')

    elif message.text == '📚 Препод':
        await Menu.teacher.set()
        await message.reply('Введите имя и/или фамилию преподавателя (лучше фамилию, например, Kubacek, vargova)')

    elif message.text == '📚 Аудитория':
        await Menu.audience.set()
        await message.reply('Введите название аудитории (I-H6, H6, h6)')

    elif message.text == '🔙 Назад':
        await Menu.start.set()
        await message.reply('Что тебе нужно?', reply_markup=StartMenu().get_keyboard())


# Create handler for '📝 Помощь' button
@dp.message_handler(state=Menu.start)
async def process_help(message: types.Message, state: FSMContext):
    logger.info('User {} asked for help'.format(message.from_user.id))

    if message.text == '📝 Помощь':
        await Menu.guide.set()
        await message.reply('Я бот для расписания UK. Я могу показать тебе расписание группы, преподавателя или аудитории. '
                            'Для этого нажми на кнопку "📚 Расписание" и выбери нужный тип расписания. '
                            'Если тебе нужно что-то изменить, нажми на кнопку "🔙 Назад" и выбери нужный пункт меню. '
                            'Если тебе нужно что-то узнать о боте, нажми на кнопку "📚 О боте"')
        

# Handler for the group
@dp.message_handler(state=Menu.group)
async def process_group(message: types.Message, state: FSMContext):
    logger.info('Processing group {}'.format(message.text))

    # try:
        # Get the url of the group
    url = URL + f'kruzky/{message.text}.csv'
    # Get data from the cache if it exists
    get_data('group', message.text, DRIVER, url, r)
    await save_to_db(url, message.from_user.first_name)
    logger.info('Group request was saved to database')
    logger.info('Group {} was cached successfully'.format(message.text))
    await message.reply_document(open('schedule.html', 'rb'))
        # await Menu.schedule.set()
    # except IndexError:
    #     logger.info('Group {} was not found'.format(message.text))
    #     await message.reply('Группа не найдена')
    # await Menu.schedule.set()

# Handler for the teacher
@dp.message_handler(state=Menu.teacher)
async def process_teacher(message: types.Message, state: FSMContext):
    logger.info('Processing teacher {}'.format(message.text))

    # Check if the teacher name is correct
    if not re.match(r'^[a-zA-Z]+$', message.text):
        await message.reply('Неверный формат преподавателя. Попробуйте еще раз')
        return
    
    # Start a new Chrome session 
    driver = webdriver.Chrome(service=service, options=options)
    try:
        logger.info('Teacher {} was cached successfully'.format(message.text))
        url = get_data('teacher', message.text, driver, URL, r)

        await save_to_db(url, message.from_user.first_name)
        logger.info('Teacher request was saved to database')

        await message.reply_document(open('schedule.html', 'rb'))

    except NoSuchElementException:
        logger.info('Teacher {} was not found'.format(message.text))

        await message.reply('Преподаватель не найден')
    await Menu.schedule.set()

# Handler for the audience
@dp.message_handler(state=Menu.audience)
async def process_audience(message: types.Message, state: FSMContext):
    logger.info('Processing audience {}'.format(message.text))

    # Initialize a new Chrome session
    driver = webdriver.Chrome(service=service, options=options)
    try:
        logger.info('Audience {} was cached successfully'.format(message.text))
        url = get_data('audience', message.text, driver, URL, r)

        await save_to_db(url, message.from_user.first_name)
        logger.info('Audience request was saved to database')

        # Write the schedule to the file
        await message.reply_document(open('schedule.html', 'rb'))

    except NoSuchElementException:
        logger.info('Audience {} was not found'.format(message.text))
        await message.reply('Аудитория не найдена')
    await Menu.schedule.set()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)