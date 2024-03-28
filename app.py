import os
import json
import telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# The messageHandler is used for all message updates
import configparser
import logging
import redis
from flask import Flask, request, jsonify

global redis1
app = Flask(__name__)

# import subprocess
# import redis_server
# subprocess.Popen([redis_server.REDIS_SERVER_PATH])
# from gptbot import HKBU_GPT


@app.route('/')
def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('/config.ini')
    print(config['TELEGRAM']['ACCESS_TOKEN'])
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    # updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']),
                         password=(config['REDIS']['PASSWORD']),
                         port=(config['REDIS']['REDISPORT']))
    # You can set this logging module,
    # so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    # register a dispatcher to handle message:
    # here we register an echo dispatcher
    # echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    # dispatcher.add_handler(echo_handler)
    global chatgpt
    # chatgpt = HKBU_GPT(config)
    chatgpt = HKBU_GPT()
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add", addUserInfo))
    dispatcher.add_handler(CommandHandler("menu", getMenu))
    dispatcher.add_handler(CommandHandler("brand", getBrand))
    dispatcher.add_handler(CommandHandler("recommend", getRecommendList))
    dispatcher.add_handler(CommandHandler("man", man))
    dispatcher.add_handler(CallbackQueryHandler(button_click))

    # To start the bot:
    updater.start_polling()
    updater.idle()


def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


def equiped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("context :" + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


def start(update: Update, context: CallbackContext) -> None:
    try:
        update.message.reply_text('Wellcome to use our robot. I will provide you with ordering assistance for Heytea😁')
        chat_id = update.effective_chat.id
        # print(chat_id)
        photo_path = './pic/Heytea.jpg'
        # print(photo_path)
        context.bot.send_photo(chat_id=chat_id, photo=open(photo_path, 'rb'))
    except (IndexError, ValueError):
        update.message.reply_text('Something error')

def getRecommendList(update: Update, context: CallbackContext) -> None:
    try:
        global redis1
        msg = redis1.get('Recommend')
        msg = str(msg, encoding='utf-8')
        format_msg = ',\n'.join(msg.split(','))
        print(format_msg)
        update.message.reply_text(format_msg)
        update.message.reply_text('https://www.youtube.com/watch?v=sPBpg-u3CRQ')
    except (IndexError, ValueError):
        update.message.reply_text('Something error')


def getBrand(update: Update, context: CallbackContext) -> None:
    try:
        global redis1
        msg = redis1.get('Brand introduction')
        update.message.reply_text(str(msg, encoding='utf-8'))
        update.message.reply_text('https://www.youtube.com/watch?v=OUauKtSa5q0')
    except (IndexError, ValueError):
        update.message.reply_text('Something error')

def addUserInfo(update: Update, context: CallbackContext) -> None:
    try:
        global redis1
        # print(str(update['message']['chat']))
        # update_id = str(update['update_id'])
        first_name = str(update['message']['chat']['first_name'])
        last_name = str(update['message']['chat']['last_name'])
        user_id = str(update['message']['chat']['id'])
        user_info = 'Name:' + first_name + last_name + '&User ID:' + user_id
        user_name = first_name + last_name
        # print(user_info)
        # str(update)(context.args[0])
        # user = user_info.args[0]  # /add keyword <-- this should store the keyword
        # redis1.incr(user)
        redis1.set(user_name, user_id)
        # print(redis1.get(user_name))
        update.message.reply_text('Your information ' + user_info + ' has already stored ')
    except (IndexError, ValueError):
        update.message.reply_text('Something error')


def man(update: Update, context: CallbackContext) -> None:
    try:
        global redis1
        update.message.reply_text('What can I say?')
    except (IndexError, ValueError):
        update.message.reply_text('Something error')


def getMenu(update: Update, context: CallbackContext) -> None:
    try:
        text = 'Which drink do you want to know?'
        chat_id = update.effective_chat.id
        buttons = [
            [InlineKeyboardButton("Boba Milk Tea", callback_data='Boba Milk Tea')],
            [InlineKeyboardButton("Classic Milk Tea", callback_data='Classic Milk Tea')],
            [InlineKeyboardButton("Green Milk Tea", callback_data='Green Milk Tea')],
            [InlineKeyboardButton("Matcha Latte", callback_data='Matcha Latte')],
            [InlineKeyboardButton("Taro Milk Tea", callback_data='Taro Milk Tea')],
            [InlineKeyboardButton("Zhizhiberry", callback_data='Zhizhiberry')],
            [InlineKeyboardButton("Succulent grapes", callback_data='Succulent grapes')],
            [InlineKeyboardButton("Succulent mango nectar", callback_data='Succulent mango nectar')]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=chat_id, text = text, reply_markup=reply_markup)
    except (IndexError, ValueError):
        update.message.reply_text('Something error')

def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    # query.edit_message_text(text=f"Selected option: {query.data}")
    # logging.info({query.data})
    global redis1
    drinkName_string = ','.join(str(item) for item in {query.data})
    # print(drinkName_string)
    msg = redis1.get(drinkName_string)
    query.edit_message_text('Comment of ' + drinkName_string + ' is below.' + str(msg, encoding='utf-8'))

    chat_id = update.effective_chat.id
    # print(chat_id)
    photo_path = './pic/' + drinkName_string + '.jpg'
    # print(photo_path)
    context.bot.send_photo(chat_id=chat_id, photo=open(photo_path, 'rb'))



class HKBU_GPT():
    def __init__(self, config='/config.ini'):
        if type(config) == str:
            self.config = configparser.ConfigParser()
            self.config.read(config)
        elif type(config) == configparser.ConfigParser:
            self.config = config

    def submit(self, message):
        conversation = [{"role": "user", "content": message}]
        url = (self.config['CHATGPT']['BASICURL']) + "/deployments/" + (
        self.config['CHATGPT']['MODELNAME']) + "/chat/completions/?api-version=" + (
              self.config['CHATGPT']['APIVERSION'])
        # url = (os.environ['BASICURL']) + "/deployments/" + (os.environ['MODELNAME']) + "/chat/completions/?api-version=" + (os.environ['APIVERSION'])
        headers = {'Content-Type': 'application/json', 'api-key': (self.config['CHATGPT']['ACCESS_TOKEN'])}
        # headers = { 'Content-Type': 'application/json', 'api-key': (os.environ['GPT_ACCESS_TOKEN']) }
        payload = {'messages': conversation}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return 'Error:', response

# def find_local_port(): 
#     import socket 
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
#     s.bind(('localhost', 0)) 
#     address, port = s.getsockname() 
#     s.close() 
#     return port

if __name__ == '__main__':
    app.run(host="158.182.163.34", port=1280)
    # local_port = find_local_port()
    # print("Local port:", local_port) 
    