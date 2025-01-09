
import telebot
import schedule
import pymongo
import time
import os
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from threading import Thread
from telebot import types
from pymongo import MongoClient

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


@myBot.message_handler(commands=['test'])
def testMessage(message):
    client = connectToDB()
    db = client.admin
    myBot.send_message(message.chat.id, db.list_collection_names(include_system_collections=False))

@myBot.message_handler(commands=['createData'])
def createData(message):
    client = connectToDB()
    db = client.admin
    list_of_collections = db.list_collection_names()  # Return a list of collections in 'test_db'
    if "internetData" not in list_of_collections:
        db.create_collection("internetData")
    
    currentCollection = db["internetData"]
    newDocument = {
        "name": "остаток",
        "cost": 199
    }
    try:
        currentCollection.insert_one(newDocument)
        myBot.send_message(message.chat.id, 'Я создал тебе документ')
    except OSError as err:
         myBot.send_message(message.chat.id, f"Ошибка в создании документа {err=}")


@myBot.message_handler(commands=['removeData'])
def removeData(message):
    client = connectToDB()
    db = client.admin
    currentCollection = db["internetData"]
    try:
        currentCollection.remove({"name": "остаток"})
        myBot.send_message(message.chat.id, 'Я очистил данные')
    except OSError as err:
        myBot.send_message(message.chat.id, f"Ошибка в очистке данных {err=}")


@myBot.message_handler(content_types=['text'])
def get_text_messages(message):

    if message.text == '👋 Поздороваться':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
        btn1 = types.KeyboardButton('Получить остаток интернет-счета')
        markup.add(btn1)
        myBot.send_message(message.from_user.id, '❓ Задайте интересующий вас вопрос', reply_markup=markup) #ответ бота

    elif message.text == 'Получить остаток интернет-счета':
        getStatMessage(message)

@myBot.message_handler(commands=['getValue'])
def getStatMessage(message):
    currentValue = getData()
    myBot.send_message(message.chat.id, f"Сейчас на счету {str(currentValue)} р.")


def send_stat():
    currentStat = get_stat()
    message = 'На интернет-счете сегодня: ' + str(currentStat) + ' р.'
    if float(currentStat) < 100.0:
        message+= 'Пора класть деньги!' 
        
    myBot.send_message(chat_id, message)

def connectToDB():
    userName = os.environ.get("MONGO_MONGO_INITDB_ROOT_USERNAME")
    password = os.environ.get("MONGO_MONGO_INITDB_ROOT_PASSWORD")
    client = MongoClient(
    host = 'mongodb://94.26.239.216:22238',
    serverSelectionTimeoutMS = 3000, # 3 second timeout
    username=userName,
    password=password,
    )
    return client

def dataUpdate():
    client = connectToDB()
    db = client.admin
    currentCollection = db["internetData"]
    try:
        currentCollection.remove({"name": "остаток"})
        myBot.send_message(message.chat.id, 'Я очистил данные')
    except OSError as err:
        myBot.send_message(message.chat.id, f"Ошибка в очистке данных {err=}")

def getData():
    client = connectToDB()
    db = client.admin
    currentCollection = db["internetData"]
    answer = ""
    currentDoc = currentCollection.find_one({"name": "остаток"})
    lastCost = currentDoc["cost"]
    return lastCost

scheduler = BlockingScheduler(timezone="Europe/Moscow") 
scheduler.add_job(send_stat, "cron", hour=9)

def schedule_checker():
    
    while True:
        scheduler.start()

Thread(target=schedule_checker).start() # Notice that you refer to schedule_checker function which starts the job

myBot.polling() # Also notice that you need to include polling to allow your bot to get commands from you. But it should happen AFTER threading!
