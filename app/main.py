
import telebot

myBot = telebot.TeleBot('')



@myBot.message_handler(commands=['start'])
def startMessage(message):
    myBot.send_message(message.chat.id, "Hello, world!")

myBot.infinity_polling()