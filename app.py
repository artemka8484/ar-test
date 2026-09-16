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
        return "Отсканируйте код"
    
    if qr_id not in db:
        bot_link = "https://t.me/my_magic_ar_bot?start=" + str(qr_id)
        return redirect(bot_link)
    
    video = db[qr_id]
    return "Плеер готов! Видео: " + video

@app.route('/webhook', methods=['POST'])
def webhook():
    # Надежный способ получения данных
    json_str = request.get_data().decode('utf-8')
    print("Получено сообщение от Telegram:", json_str) # Маячок в логи
    
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(commands=['start'])
def start_command(message):
    print("Бот начал отвечать!") # Маячок в логи
    text = message.text.split()
    if len(text) > 1:
        qr_id = text[1]
        markup = InlineKeyboardMarkup()
        b1 = InlineKeyboardButton("Видео 1", callback_data="bind_" + qr_id + "_v1")
        b2 = InlineKeyboardButton("Видео 2", callback_data="bind_" + qr_id + "_v2")
        markup.add(b1, b2)
        bot.send_message(message.chat.id, "Код: " + qr_id + "\nВыберите видео:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Жду сканирования QR-кода.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('bind_'))
def callback_query(call):
    parts = call.data.split('_')
    qr_id = parts[1]
    v_name = parts[2]
    
    links = {"v1": "Космос", "v2": "Природа"}
    db[qr_id] = links[v_name]
    
    bot.answer_callback_query(call.id, "Готово!")
    msg = "Видео '" + links[v_name] + "' привязано к коду " + qr_id
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
