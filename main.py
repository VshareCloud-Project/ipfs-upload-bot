import os
import sys
import telebot
import configloader
import requests
import urllib
import logging
import uuid
import time
from logging import handlers
c = configloader.config()
logging.basicConfig(
    level=getattr(logging,c.getkey("log_level")), format="%(asctime)s [%(levelname)s][%(pathname)s:%(lineno)d]: %(message)s"
)
file_log_handler = handlers.RotatingFileHandler(c.getkey("log_file"), mode="a", encoding="utf-8", maxBytes=10 * 1024 * 1024, backupCount=5)
formatter = logging.Formatter("%(asctime)s [%(levelname)s][%(pathname)s:%(lineno)d]: %(message)s")
file_log_handler.setFormatter(formatter)
logging.getLogger('').addHandler(file_log_handler)
if c.getkey("telegram_bot_server") != "" and c.getkey("telegram_bot_server") is not None:
    from telebot import apihelper
    apihelper.API_URL = c.getkey("telegram_bot_server")
    fileurl = c.getkey("telegram_bot_server_file")
else:
    c.setkey("telegram_bot_server", "https://api.telegram.org/bot{0}/{1}")
    fileurl = "https://api.telegram.org/file/bot{0}".format(c.getkey("telegram_api_token"))
    #c.reload()
bot = telebot.TeleBot(c.getkey("telegram_api_token"))
def genuuid():
    ouid = uuid.uuid5(uuid.NAMESPACE_DNS, c.getkey("secret_key")+str(time.time()))
    okey = str(ouid)
    return okey

@bot.message_handler(content_types=['document','audio','video'])
def handle_docs(message):
    stype =message.content_type
    file_size = getattr(message,stype).file_size
    if file_size > c.getkey("maxium_size"):
        bot.reply_to(message, "File size is too big")
        return
    file_info = bot.get_file(getattr(message,stype).file_id)
    #file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(c.getkey("telegram_api_token"), file_info.file_path))
    dl_url =  fileurl +"/"+ file_info.file_path
    nuuid = genuuid() + ".ibin"
    with requests.get(dl_url, stream=True,timeout=c.getkey("timeout")) as req:
        with open(os.path.join(c.getkey("tmp_path"),nuuid), 'wb') as f:
            for chunk in req.iter_content(chunk_size=c.getkey("chunk_size")):
                if chunk:
                    f.write(chunk)
    #params = urllib.parse.urlencode({"pin":True,"path":dl_url}, quote_via=urllib.parse.quote)
    ret = requests.post(c.getkey("ipfs_api_host")+"/api/v0/add?pin=true", files={'file': open(os.path.join(c.getkey("tmp_path"),nuuid), 'rb')},timeout=c.getkey("timeout"))
    if ret.status_code != 200:
        bot.reply_to(message, "Error: "+ret.text)
        return
    else:
        ret = ret.json()
        if "Hash" in ret:
            bot.reply_to(message, "Your CID is "+ret["Hash"])
        else:
            bot.reply_to(message, "Error: "+ret)
    try:
        os.remove(os.path.join(c.getkey("tmp_path"),nuuid))
    except FileNotFoundError:
        pass

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_size = message.photo[-1].file_size
    if file_size > c.getkey("maxium_size"):
        bot.reply_to(message, "File size is too big")
        return
    file_info = bot.get_file(message.photo[-1].file_id)
    #file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(c.getkey("telegram_api_token"), file_info.file_path))
    dl_url = fileurl +"/"+ file_info.file_path
    nuuid = genuuid() + ".ibin"
    with requests.get(dl_url, stream=True,timeout=c.getkey("timeout")) as req:
        with open(os.path.join(c.getkey("tmp_path"),nuuid), 'wb') as f:
            for chunk in req.iter_content(chunk_size=c.getkey("chunk_size")):
                if chunk:
                    f.write(chunk)
    #params = urllib.parse.urlencode({"pin":True,"path":dl_url}, quote_via=urllib.parse.quote)
    ret = requests.post(c.getkey("ipfs_api_host")+"/api/v0/add?pin=true", files={'file': open(os.path.join(c.getkey("tmp_path"),nuuid), 'rb')},timeout=c.getkey("timeout"))
    if ret.status_code != 200:
        bot.reply_to(message, "Error: "+ret.text)
        return
    else:
        ret = ret.json()
        if "Hash" in ret:
            bot.reply_to(message, "Your CID is "+ret["Hash"])
        else:
            bot.reply_to(message, "Error: "+ret)
    try:
        os.remove(os.path.join(c.getkey("tmp_path"),nuuid))
    except FileNotFoundError:
        pass
bot.infinity_polling()
list_file = os.listdir(c.getkey("tmp_path"))
for file in list_file:
    if file.endswith(".ibin"):
        try:
            os.remove(os.path.join(c.getkey("tmp_path"),file))
        except FileNotFoundError:
            pass
