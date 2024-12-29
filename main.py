
import telebot
import schedule
import time
import os
import logging

message_time = os.environ.get("TIME")

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
    currentValue = startValue - everyDayCost
    os.environ["STARTVALUE"] = currentValue
    return str(currentValue)


def send_stat():
    currentStat = get_stat()
    message = 'На интернет счете сегодня: {currentStat} р.'
    if currentStat < 100:
        message+= 'Пора класть деньги!' 
        
    myBot.send_message(chat_id, message)


schedule.every().day.at(str(message_time)).do(send_stat)

#while True:
 #   schedule.run_pending()
  #  time.sleep(5)

myBot.infinity_polling()