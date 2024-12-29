
import telebot
import schedule
import time
import os
import logging

message_time = os.environ.get("TIME")
CHANNEL_NAME = '@Snezzzz_bot'

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
    message = 'На интернет счете сегодня: {currentStat} р.'
    if float(currentStat) < 100.0:
        message+= 'Пора класть деньги!' 
        
    myBot.send_message(CHANNEL_NAME, message)


schedule.every(5).seconds.do(send_stat)  

while True:  
    schedule.run_pending() 

myBot.infinity_polling()