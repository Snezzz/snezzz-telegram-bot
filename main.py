
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
from bson import ObjectId

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
    btn2 = types.KeyboardButton("Пометить задачу выполненной")
    markup.add(btn1, btn2)
    myBot.send_message(message.chat.id, "Привет! Я твой бот-помощник", reply_markup=markup)

@myBot.message_handler(commands=['test'])
def testMessage(message):
    send_stat()

###################################################
################# Tasks collection ################
###################################################
@myBot.message_handler(commands=['createTasksCollection'])
def createTasksCollection(message):
    client = connectToDB()
    db = client.admin
    list_of_collections = db.list_collection_names()  # Return a list of collections in 'test_db'
    if "myTasks" not in list_of_collections:
        try:
         db.create_collection("myTasks")
         myBot.send_message(message.chat.id, 'Я создал коллекцию задач')
        except OSError as err:
         myBot.send_message(message.chat.id, f"Ошибка при создании коллекции {err=}")

@myBot.message_handler(commands=['setTask'])
def setTask(message):
    client = connectToDB()
    db = client.admin
    currentCollection = db["myTasks"]
    documentsCount = currentCollection.count_documents({})
    newDocument = {
        "number": (documentsCount + 1),
        "text": "ex",
        "completed": False
    }
    try:
        currentCollection.insert_one(newDocument)
        myBot.send_message(message.chat.id, 'Я создал тебе задачу')
    except OSError as err:
        myBot.send_message(message.chat.id, f"Ошибка в создании задачи {err=}")

def setTaskCompleted(message):
    client = connectToDB()
    db = client.admin
    currentCollection = db["myTasks"]
    query = {
        "text": message.text
    }
   
    try:
        doc = currentCollection.find_one(query)
        if doc != None:
            docID = doc["_id"]
            currentCollection.find_one_and_update(
            {"_id" : ObjectId("")},
            {"$set":
            {"completed": True}},upsert=True)
            myBot.send_message(message.chat.id, 'Я пометил задачу как выполненная')
        else:
            myBot.send_message(message.chat.id, 'Задача не найдена')
    except OSError as err:
         myBot.send_message(message.chat.id, f"Ошибка в обновлении задачи {err=}")

@myBot.message_handler(commands=['getAllTasks'])
def getAllTasks(message):
    client = connectToDB()
    db = client.admin
    currentCollection = db["myTasks"]
    answer = ""
    for task in currentCollection.find():
        answer = answer + str(task["number"]) + ". " + str(task["text"])
        if task["completed"]:
            answer += " (выполнена)"
        answer += "\n"
    if answer == "":
        answer = "Нет данных"

    myBot.send_message(message.chat.id, answer)

@myBot.message_handler(commands=['getActualTasks'])
def getActualTasks(message):
    client = connectToDB()
    db = client.admin
    currentCollection = db["myTasks"]
    answer = ""
    for task in currentCollection.find():
        if not task['completed']:
            answer = answer + str(task["number"]) + ". " + str(task["text"]) + "\n"
    
    if answer == "":
        answer = "Нет данных"

    myBot.send_message(message.chat.id, answer)

@myBot.message_handler(commands=['getCompletedTasks'])
def getCompletedTasks(message):
    client = connectToDB()
    db = client.admin
    currentCollection = db["myTasks"]
    answer = ""
    for task in currentCollection.find():
        if task['completed']:
            answer = answer + str(task["number"]) + ". " + str(task["text"]) + "\n"
    
    if answer == "":
        answer = "Нет данных"

    myBot.send_message(message.chat.id, answer)

###################################################
################# /Tasks collection ###############
###################################################

###################################################
######### Internet-data collection ################
###################################################
@myBot.message_handler(commands=['createData'])
def createData(message):
    client = connectToDB()
    db = client.admin
    list_of_collections = db.list_collection_names()  # Return a list of collections in 'test_db'
    if "internetData" not in list_of_collections:
        db.create_collection("internetData")
    
    currentCollection = db["internetData"]
    value = os.environ.get("STARTVALUE")
    newDocument = {
        "name": "остаток",
        "cost": float(value)
    }
    try:
        currentCollection.insert_one(newDocument)
        myBot.send_message(message.chat.id, 'Я создал тебе документ')
    except OSError as err:
         myBot.send_message(message.chat.id, f"Ошибка в создании документа {err=}")

@myBot.message_handler(commands=['getList'])
def getList(message):
    client = connectToDB()
    db = client.admin
    currentCollection = db["internetData"]
    answer = ""
    for doc in currentCollection.find():
        answer = answer + str(doc["name"]) + " : " + str(doc["cost"]) + "\n"
    if answer == "":
        answer = "Нет данных"

    myBot.send_message(message.chat.id, answer)
    
@myBot.message_handler(commands=['removeData'])
def removeData(message):
    client = connectToDB()
    db = client.admin
    currentCollection = db["internetData"]
    try:
        currentCollection.delete_many({"name": "остаток"})
        myBot.send_message(message.chat.id, 'Я очистил данные')
    except OSError as err:
        myBot.send_message(message.chat.id, f"Ошибка в очистке данных {err=}")

@myBot.message_handler(commands=['getValue'])
def getStatMessage(message):
    currentValue = round(float(getData()),3)
    myBot.send_message(message.chat.id, f"Сейчас на счету {str(currentValue)} р.")

def send_stat():
    currentStat = round(float(getData()),3)
    message = 'На интернет-счете сегодня: ' + str(currentStat) + ' р.'
    if float(currentStat) < 100.0:
        message+= '\n'+'Пора класть деньги!' 
    reduce(currentStat)    
    myBot.send_message(chat_id, message)

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

def reduce(currentValue):
    everyDayCost = os.environ.get("EVERYDAYCOST")
    value = float(currentValue) - float(everyDayCost)
    client = connectToDB()
    db = client.admin
    currentCollection = db["internetData"]
    currentCollection.delete_many({"name": "остаток"}) 
    newDoc = {
        "name": "остаток",
        "cost": value
    }
      
    currentCollection.insert_one(newDoc)

###################################################
######### /Internet-data collection ###############
###################################################

@myBot.message_handler(commands = ['meow'])
def meowFunc(message):
    url = getUrl()
    mybot.send_photo(message.chat.id, url)

def getUrl():
    contents = requests.get('https://thatcopy.pw/catapi/rest/').json()
    image_url = contents['url']
    return image_url


@myBot.message_handler(content_types=['text'])
def get_text_messages(message):

    if message.text == '👋 Поздороваться':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
        btn1 = types.KeyboardButton('Получить остаток интернет-счета')
        btn2 = types.KeyboardButton('Очистить данные')
        btn3 = types.KeyboardButton('Протестировать меня')
        btn4 = types.KeyboardButton('Получить все данные')
        btn5 = types.KeyboardButton('Создать новые данные')
        markup.add(btn1,btn2,btn3,btn4,btn5)
        myBot.send_message(message.from_user.id, '❓ Задайте интересующий вас вопрос', reply_markup=markup) #ответ бота
    elif message.text == 'Получить остаток интернет-счета':
        getStatMessage(message)
    elif message.text == 'Очистить данные':
        removeData(message)
    elif message.text == 'Протестировать меня':
        testMessage(message)
    elif message.text == 'Получить все данные':
        getList(message)
    elif message.text == 'Создать новые данные':
        createData(message)
    elif message.text == 'Пометить задачу выполненной':
        client = connectToDB()
        db = client.admin
        currentCollection = db["myTasks"]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
        for task in currentCollection.find():
            btn = types.KeyboardButton(task["text"])
            markup.add(btn)
        myBot.send_message(message.from_user.id, 'Выбери задачу', reply_markup=markup) #ответ бота
  
    #else: 
     #   setTaskCompleted(message)

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

scheduler = BlockingScheduler(timezone="Europe/Moscow") 
scheduler.add_job(send_stat, "cron", hour=9)

def schedule_checker():
    
    while True:
        scheduler.start()

Thread(target=schedule_checker).start() # Notice that you refer to schedule_checker function which starts the job

myBot.polling() # Also notice that you need to include polling to allow your bot to get commands from you. But it should happen AFTER threading!
