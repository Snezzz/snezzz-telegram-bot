
import telebot
import schedule
import os

myBot = telebot.TeleBot(os.environ.get("TOKEN"))


@myBot.message_handler(commands=['start'])
def startMessage(message):
    myBot.send_message(message.chat.id, "Hello, world!")

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


schedule.every().day.at('17:30').do(send_stat)

while True:
    schedule.run_pending()
    time.sleep(5)

myBot.infinity_polling()