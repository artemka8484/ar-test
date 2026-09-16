import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request, redirect

API_TOKEN = '8808815647:AAF7Bvhh0QEv1HPhIfjAu-WSyrVeB6j_FvA'
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Наша база данных (пока храним в памяти сервера)
db = {}

# Главная страница (Куда ведет QR-код)
@app.route('/')
def home():
    qr_id = request.args.get('id')
    
    if not qr_id:
        return "Пожалуйста, отсканируйте QR-код с этикетки товара."
        
    # Если видео еще не привязано -> отправляем вас в Телеграм для настройки
    if qr_id not in db:
        bot_link = f"https://t.me/my_magic_ar_bot?start={qr_id}"
        return redirect(bot_link)
        
    # Если видео уже привязано -> выдаем страницу AR-плеера для покупателя
    video_url = db[qr_id]
    return f"
