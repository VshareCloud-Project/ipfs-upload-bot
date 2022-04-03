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
    apihelper.READ_TIMEOUT = c.getkey("timeout")
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

@bot.message_handler(content_types=['document','audio','video','photo','sticker','voice','animation','video_note'])
def handle_docs(message):
    new_message = bot.reply_to(message,"Processing: 0%")
    stype =message.content_type
    try:
        file_size = getattr(message,stype).file_size
        if file_size > c.getkey("maxium_size"):
            bot.edit_message_text("File size is too big", new_message.chat.id, new_message.message_id)
            return
        n_file_id = getattr(message,stype).file_id
        
    except:
        file_size = getattr(message,stype)[-1].file_size
        if file_size > c.getkey("maxium_size"):
            bot.edit_message_text("File size is too big", new_message.chat.id, new_message.message_id)
            return
        n_file_id = getattr(message,stype)[-1].file_id
    bot.edit_message_text("Processing: 10%", new_message.chat.id, new_message.message_id)
    is_success_download = False
    for i in range(0,5):
        try:
            file_info = bot.get_file(n_file_id)
            is_success_download = True
            break
        except:
            import traceback
            logging.error(traceback.format_exc())
    if not is_success_download:
        bot.edit_message_text("Failed to download file", new_message.chat.id, new_message.message_id)
        return
    bot.edit_message_text("Processing: 40%", new_message.chat.id, new_message.message_id)
    if c.getkey("telegram_bot_server") != "" and c.getkey("telegram_bot_server") is not None and c.getkey("telegram_bot_server") != "https://api.telegram.org/bot{0}/{1}":
        newfile = file_info.file_path
        bot.edit_message_text("Processing: 70%", new_message.chat.id, new_message.message_id)
    else:
        #file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(c.getkey("telegram_api_token"), file_info.file_path))
        dl_url =  fileurl +"/"+ file_info.file_path
        nuuid = genuuid() + ".ibin"
        newfile = os.path.join(c.getkey("tmp_path"),nuuid)
        with requests.get(dl_url, stream=True,timeout=c.getkey("timeout")) as req:
            with open(os.path.join(c.getkey("tmp_path"),nuuid), 'wb') as f:
                for chunk in req.iter_content(chunk_size=c.getkey("chunk_size")):
                    if chunk:
                        f.write(chunk)
        bot.edit_message_text("Processing: 70%", new_message.chat.id, new_message.message_id)
    
    #params = urllib.parse.urlencode({"pin":True,"path":dl_url}, quote_via=urllib.parse.quote)
    ret = requests.post(c.getkey("ipfs_api_host")+"/api/v0/add?pin=true", files={'file': open(os.path.join(newfile), 'rb')},timeout=c.getkey("timeout"))
    if ret.status_code != 200:
        bot.edit_message_text("Error: "+ret.text, new_message.chat.id, new_message.message_id)
        return
    else:
        ret = ret.json()
        if "Hash" in ret:
            bot.edit_message_text("Processing: 100% , Preparing to show CID.", new_message.chat.id, new_message.message_id)
            time.sleep(0.5)
            bot.reply_to(message, "Your CID is `"+ret["Hash"]+"`\nUse @vsharecloud\_bot to keep it permanently\n使用 @vsharecloud\_bot 以永久保存文件。",parse_mode="Markdown")
        else:
            bot.edit_message_text("Error: "+ret, new_message.chat.id, new_message.message_id)
    if not (c.getkey("telegram_bot_server") != "" and c.getkey("telegram_bot_server") is not None and c.getkey("telegram_bot_server") != "https://api.telegram.org/bot{0}/{1}"):
        try:
            os.remove(os.path.join(c.getkey("tmp_path"),nuuid))
        except FileNotFoundError:
            pass
@bot.message_handler(commands=['start',"help"])
def handle_start(message):
    bot.reply_to(message, "Send me a file to add to IPFS, The file will be kept for one day, Please add the cid to @vsharecloud_bot to keep it permanently!\n给我发送文件以添加至IPFS网络，文件将保留一天，请将CID添加至 @vsharecloud_bot 以永久保存！")
bot.infinity_polling()
list_file = os.listdir(c.getkey("tmp_path"))
for file in list_file:
    if file.endswith(".ibin"):
        try:
            os.remove(os.path.join(c.getkey("tmp_path"),file))
        except FileNotFoundError:
            pass
'''        
if c.getkey("telegram_bot_server") != "" and c.getkey("telegram_bot_server") is not None and c.getkey("telegram_bot_server") != "https://api.telegram.org/bot{0}/{1}":
    bot.log_out()
'''