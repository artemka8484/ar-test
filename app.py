import telebot
from flask import Flask, request, redirect

API_TOKEN = '8808815647:AAF7Bvhh0QEv1HPhIfjAu-WSyrVeB6j_FvA'
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# База данных для тестов
db = {}

@app.route('/')
def home():
    qr_id = request.args.get('id')
    if not qr_id:
        return "Отсканируйте QR-код с этикетки."
        
    if qr_id not in db:
        bot_link = "https://t.me/my_magic_ar_bot?start=" + str(qr_id)
        return redirect(bot_link)
        
    return "Здесь будет открываться видео из Kling AI!"

# Сюда Telegram будет присылать сообщения
@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# Реакция бота на команду /start
@bot.message_handler(commands=['start'])
def start_command(message):
    text = message.text.split()
    if len(text) > 1:
        qr_id = text[1]
        bot.send_message(message.chat.id, f"Привет! Вы хотите привязать AR-видео к коду: {qr_id}?\n\n(Скоро здесь появятся кнопки выбора роликов)")
    else:
        bot.send_message(message.chat.id, "Привет! Я бот для управления AR-этикетками. Отсканируйте QR-код для начала работы.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
