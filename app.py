import os
import json
import telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext
from telegram import Update
# The messageHandler is used for all message updates
import configparser
import logging
import redis

global redis1

# import subprocess
# import redis_server
# subprocess.Popen([redis_server.REDIS_SERVER_PATH])
# from gptbot import HKBU_GPT
import requests


def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
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
    dispatcher.add_handler(CommandHandler("comment", getComment))
    dispatcher.add_handler(CommandHandler("man", man))
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
        global redis1
        msg = redis1.get('menu')
        update.message.reply_text('Menu:' + str(msg, encoding='utf-8'))
    except (IndexError, ValueError):
        update.message.reply_text('Something error')


def getComment(update: Update, context: CallbackContext) -> None:
    try:
        global redis1
        logging.info(context.args)
        comment_string = ' '.join(context.args)
        print(comment_string)
        msg = redis1.get(comment_string)
        update.message.reply_text('Comment of:' + comment_string + ' is below.' + str(msg, encoding='utf-8'))

        chat_id = update.effective_chat.id
        print(chat_id)
        photo_path = './pic/' + comment_string + '.jpg'
        # print(photo_path)
        context.bot.send_photo(chat_id=chat_id, photo=open(photo_path, 'rb'))

    except (IndexError, ValueError):
        update.message.reply_text('Something error')


class HKBU_GPT():
    def __init__(self, config='./config.ini'):
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


if __name__ == '__main__':
    main()