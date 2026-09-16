import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request, redirect

API_TOKEN = '8808815647:AAF7Bvhh0QEv1HPhIfjAu-WSyrVeB6j_FvA'
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)
db = {}

@app.route('/')
def home():
    qr_id = request.args.get('id')
    if not qr_id:
        return "Отсканируйте QR-код с этикетки."
    
    if qr_id not in db:
        bot_link = "https://t.me/my_magic_ar_bot?start=" + str(qr_id)
        return redirect(bot_link)
    
    video = db[qr_id]
    return "
