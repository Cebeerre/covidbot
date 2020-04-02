#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import logging
import minidb
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import re
from datetime import datetime
from dateutil import tz
import os

BPATH = os.environ['BPATH']
BTOKEN = os.environ['BTOKEN']

MSGDB = BPATH+'/messages.db'
URLDB = BPATH+'/urls.db'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

WHITE_URLS = ['covidwarriors.org', 'covidwarriors.io', 'zoom.us', 'uma.es', 'microsoft.com', 'http://bit.ly/covid-warriors-boletin']
TOKEN = BTOKEN
welcome_text = 'Te damos la bienvenida a CovidWarriors:\n' \
               '1) Tenemos actualizado casi en tiempo real un resumen en un BOLETÍN online disponible aquí:\n' \
               'http://bit.ly/covid-warriors-boletin\n' \
               '2) Registra tu PERFIL en la WEB http://www.covidwarriors.org y si tienes NECESIDADES o SOLUCIONES añádelas\n' \
               '3) PRESENTATE brevemente\n' \
               '4) Por favor, no generes RUIDO innecesario'
spam_text = 'Hola soy el bot de CovidWarriors, la noticia/url que has enlazado ya se mandó el {}. Por favor, ayuda a no saturar el canal. Gracias.'

from_zone = tz.tzutc()
to_zone = tz.tzlocal()
timeformat = '%Y-%m-%d %H:%M:%S'

class Message(minidb.Model):
    msg_id = int
    date = str
    username = str
    user_id = int
    user_first_name = str
    user_last_name = str
    user_is_bot = str
    chat_id = int
    chat_title = str
    chat_text = str

class urls(minidb.Model):
    url = str
    username = str
    msg_id = int
    chat_id = int
    date = str
    chat_title = str

def start(update, context):
    update.message.reply_text('Hi!')

def help(update, context):
    update.message.reply_text('Help!')

def new_member(update, context):
    update.message.reply_text(welcome_text, disable_web_page_preview=True, quote=False)

def echo(update, context):
    db = minidb.Store(MSGDB)
    db.register(Message)
    message = Message()
    message.msg_id = int(update.message.message_id)
    message.date = update.message.date
    message.username = update.message.from_user['username']
    message.user_id = int(update.message.from_user['id'])
    message.user_first_name = update.message.from_user['first_name']
    message.user_last_name = update.message.from_user['last_name']
    message.user_is_bot = update.message.from_user['is_bot']
    message.chat_id = int(update.message.chat['id'])
    message.chat_title = update.message.chat['title']
    message.chat_text = update.message.text
    db.save(message)
    db.commit()
    db.close()
    http = re.findall(r'(https?://\S+)', update.message.text)
    dbu = minidb.Store(URLDB)
    dbu.register(urls)
    url = urls()
    for i in http:
        if not any(st in i for st in WHITE_URLS):
            if not url.get(dbu, (url.c.url == i) & (url.c.chat_id == message.chat_id)):
                url.username = message.username
                url.date = message.date
                url.url = i
                url.msg_id = message.msg_id
                url.chat_id = message.chat_id
                url.chat_title = message.chat_title
                dbu.save(url)
                dbu.commit()
            else:
                urlobj = url.get(dbu, (url.c.url == i) & (url.c.chat_id == message.chat_id))
                if update.message.message_id != urlobj.msg_id:
                    ondateobj = datetime.strptime(urlobj.date,timeformat)
                    ondateutc = ondateobj.replace(tzinfo=from_zone)
                    ondatelocal = ondateutc.astimezone(to_zone)
                    datestring = ondatelocal.strftime('%Y-%m-%d a las %H:%M')
                    custom_spam = spam_text.format(datestring)
                    update.message.reply_text(custom_spam)
    dbu.close()

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
