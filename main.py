
import telebot
import schedule
import time
import os
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from threading import Thread
from telebot import types


message_time = os.environ.get("TIME")
chat_id = os.environ.get("CHAT_ID")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


myBot = telebot.TeleBot(os.environ.get("TOKEN"))


@myBot.message_handler(commands=['start'])
def startMessage(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Поздороваться")
    markup.add(btn1)
    myBot.send_message(message.chat.id, "Привет! Я твой бот-помощник", reply_markup=markup)


@myBot.message_handler(content_types=['text'])
def get_text_messages(message):

    if message.text == '👋 Поздороваться':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
        btn1 = types.KeyboardButton('Получить остаток интернет-счета')
        markup.add(btn1)
        myBot.send_message(message.from_user.id, '❓ Задайте интересующий вас вопрос', reply_markup=markup) #ответ бота

    elif message.text == 'Получить остаток интернет-счета':
        getStatMessage(message)

@myBot.message_handler(commands=['get_stat'])
def getStatMessage(message):
    val = get_stat()
    myBot.send_message(message.chat.id, str(val))


def get_stat():
    everyDayCost = os.environ.get("EVERYDAYCOST")
    datafile = open("data.txt", "w+")
    startValue = datafile.readline() 
   # currentValue = float(startValue) - float(everyDayCost)
    return str(startValue)

def send_stat():
    currentStat = get_stat()
    message = 'На интернет-счете сегодня: ' + str(currentStat) + ' р.'
    if float(currentStat) < 100.0:
        message+= 'Пора класть деньги!' 
        
    myBot.send_message(chat_id, message)

scheduler = BlockingScheduler(timezone="Europe/Moscow") 
scheduler.add_job(send_stat, "cron", hour=9)

def schedule_checker():
    
    while True:
        scheduler.start()

Thread(target=schedule_checker).start() # Notice that you refer to schedule_checker function which starts the job

myBot.polling() # Also notice that you need to include polling to allow your bot to get commands from you. But it should happen AFTER threading!
