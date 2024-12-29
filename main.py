
import telebot
import schedule
import time
import os
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from threading import Thread


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
    myBot.send_message(message.chat.id, "Hello, world!")

@myBot.message_handler(commands=['get_stat'])
def getStatMessage(message):
    val = get_stat()
    myBot.send_message(message.chat.id, str(val))


def get_stat():
    everyDayCost = os.environ.get("EVERYDAYCOST")
    startValue = os.environ.get("STARTVALUE")
    currentValue = float(startValue) - float(everyDayCost)
    os.environ["STARTVALUE"] = str(currentValue)
    return str(currentValue)

def send_stat():
    currentStat = get_stat()
    message = 'На интернет счете сегодня: ' + str(currentStat) + ' р.'
    if float(currentStat) < 100.0:
        message+= 'Пора класть деньги!' 
        
    myBot.send_message(chat_id, message)

scheduler = BlockingScheduler(timezone="Europe/Berlin") 
scheduler.add_job(send_stat, "cron", hour=23)

#schedule.every(10).seconds.do(send_stat)
#schedule.every().day.at(":10").do(send_stat)  - not working

def schedule_checker():
    
    while True:
        scheduler.start()

Thread(target=schedule_checker).start() # Notice that you refer to schedule_checker function which starts the job

myBot.polling() # Also notice that you need to include polling to allow your bot to get commands from you. But it should happen AFTER threading!

#myBot.infinity_polling()