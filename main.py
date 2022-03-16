import telebot
import configloader
import requests
c = configloader.config()
bot = telebot.TeleBot(c.getkey("telegram_api_token"))
@bot.message_handler(content_types=['document','audio','video'])
def handle_docs(message):
    stype =message.content_type
    file_size = getattr(message,stype).file_size
    if file_size > c.getkey("maxium_size"):
        bot.reply_to(message, "File size is too big")
        return
    file_info = bot.get_file(getattr(message,stype).file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(c.getkey("telegram_api_token"), file_info.file_path))
    ret = requests.post(c.getkey("ipfs_api_host")+"/api/v0/add?pin=true", files={'file': file.content})
    if ret.status_code != 200:
        bot.reply_to(message, "Error: "+ret.text)
        return
    else:
        ret = ret.json()
        if "Hash" in ret:
            bot.reply_to(message, "Your CID is "+ret["Hash"])
        else:
            bot.reply_to(message, "Error: "+ret)
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_size = message.photo[-1].file_size
    if file_size > c.getkey("maxium_size"):
        bot.reply_to(message, "File size is too big")
        return
    file_info = bot.get_file(message.photo[-1].file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(c.getkey("telegram_api_token"), file_info.file_path))
    ret = requests.post(c.getkey("ipfs_api_host")+"/api/v0/add?pin=true", files={'file': file.content})
    if ret.status_code != 200:
        bot.reply_to(message, "Error: "+ret.text)
        return
    else:
        ret = ret.json()
        if "Hash" in ret:
            bot.reply_to(message, "Your CID is "+ret["Hash"])
        else:
            bot.reply_to(message, "Error: "+ret)
bot.infinity_polling()

