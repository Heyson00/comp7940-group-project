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
# ss
# from gptbot import HKBU_GPT
import requests


def main():
    # Load your token and create an Updater for your Bot
    # config = configparser.ConfigParser()
    # config.read('config.ini')
    # print(config['TELEGRAM']['ACCESS_TOKEN'])
    # updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    updater = Updater(token='TELEGRAM_ACCESS_TOKEN', use_context=True)
    # updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    global redis1
    redis1 = redis.Redis(host='REDIS_HOST',
                         password='REDIS_PASSWORD',
                         port='REDIS_PORT')
    # redis1 = redis.Redis(host=(config['REDIS']['HOST']),
    # password=(config['REDIS']['PASSWORD']),
    # port=(config['REDIS']['REDISPORT']))

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
    dispatcher.add_handler(CommandHandler("add", add))
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


def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]  # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text('You have said ' + msg + ' for ' +
                                  redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')


class HKBU_GPT():
    # def __init__(self, config='./config.ini'):
    # def __init__(self, config='./config.ini'):
    #     if type(config) == str:
    #         self.config = configparser.ConfigParser()
    #         self.config.read(config)
    #     elif type(config) == configparser.ConfigParser:
    #         self.config = config
        # pass

    def submit(self, message):
        conversation = [{"role": "user", "content": message}]
        # url = (self.config['CHATGPT']['BASICURL']) + "/deployments/" + (self.config['CHATGPT']['MODELNAME']) + "/chat/completions/?api-version=" + (self.config['CHATGPT']['APIVERSION'])
        url = 'CHATGPT_BASICURL' + "/deployments/" + 'CHATGPT_MODELNAME' + "/chat/completions/?api-version=" + (
        'CHATGPT_APIVERSION')
        # url = (os.environ['BASICURL']) + "/deployments/" + (os.environ['MODELNAME']) + "/chat/completions/?api-version=" + (os.environ['APIVERSION'])
        headers = {'Content-Type': 'application/json', 'api-key': 'CHATGPT_ACCESS_TOKEN'}
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