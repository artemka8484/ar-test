Python
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton as Btn
from flask import Flask, request, redirect

API_TOKEN = '8808815647:AAF7Bvhh0QEv1HPhIfjAu-WSyrVeB6j_FvA'
bot = telebot.TeleBot(API_TOKEN, threaded=False)
app = Flask(__name__)
db = {}
users = {}
@app.route('/')
def home():
    qr_id = request.args.get('id')
    if not qr_id:
        return "Отсканируйте код"
    if qr_id not in db:
        link = "https://t.me/my_magic_ar_bot?start=" + str(qr_id)
        return redirect(link)
    data = db[qr_id]
    html = "
AR Сцена (" + str(data.get('lang', 'ru')) + ")
\n"
if data.get('vid'):
html += "
🎥 Видео: " + str(data['vid']) + "
\n"
if data.get('tst'):
html += "
🥂 Тосты: " + ", ".join(data['tst']) + "
\n"
if data.get('gam'):
html += "
🎮 Игра: " + str(data['gam']) + "
\n"
return html
🎥 Видео: " + str(data['vid']) + "
"
if data.get('tst'):
html = html + "
🥂 Тосты: " + ", ".join(data['tst']) + "
"
if data.get('gam'):
html = html + "
🎮 Игра: " + str(data['gam']) + "
"
return html
@app.route('/webhook', methods=['POST'])
def webhook():
json_str = request.get_data().decode('utf-8')
update = telebot.types.Update.de_json(json_str)
bot.process_new_updates([update])
return "OK", 200
def get_hub_menu(uid):
k = InlineKeyboardMarkup(row_width=1)
if not users[uid].get('vid'):
k.add(Btn("🎥 Прикрепить видео", callback_data="hub_vid"))
if not users[uid].get('tst'):
k.add(Btn("🥂 Прикрепить тосты", callback_data="hub_tst"))
if not users[uid].get('gam'):
k.add(Btn("🎮 Прикрепить игру", callback_data="hub_gam"))
if users[uid].get('vid') or users[uid].get('tst') or users[uid].get('gam'):
    k.add(Btn("✅ Подтвердить", callback_data="hub_done"))
    k.add(Btn("🔄 Начать сначала", callback_data="hub_reset"))
return k
@bot.message_handler(commands=['start'])
def start_command(message):
uid = message.chat.id
text = message.text.split()
if len(text) > 1:
qr_id = text[1]
users[uid] = {'qr': qr_id, 'lang': None, 'vid': None, 'tst': [], 'gam': None}
    k = InlineKeyboardMarkup(row_width=1)
    k.add(
        Btn("🇲🇪 Crnogorski", callback_data="lang_cr"),
        Btn("🇬🇧 English", callback_data="lang_en"),
        Btn("🇷🇺 Русский", callback_data="lang_ru")
    )
    bot.send_message(uid, "Настройка кода: " + qr_id + "\n\nВыберите язык:", reply_markup=k)
else:
    bot.send_message(uid, "Жду сканирования QR-кода.")
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
uid = call.message.chat.id
data = call.data
if uid not in users:
    bot.answer_callback_query(call.id, "Ошибка! Отсканируйте код заново.")
    return
if data.startswith("lang_"):
    users[uid]['lang'] = data.split('_')[1]
    bot.edit_message_text("Главное меню. Выберите, что хотите прикрепить:", uid, call.message.message_id, reply_markup=get_hub_menu(uid))
elif data == "hub_reset":
    qr_id = users[uid]['qr']
    users[uid] = {'qr': qr_id, 'lang': None, 'vid': None, 'tst': [], 'gam': None}
    bot.edit_message_text("Сброшено. Выберите язык:", uid, call.message.message_id, reply_markup=InlineKeyboardMarkup().add(Btn("🇷🇺 Русский", callback_data="lang_ru")))
elif data == "hub_done":
    qr_id = users[uid]['qr']
    db[qr_id] = users[uid]
    del users[uid]
    bot.edit_message_text("Готово! Всё привязано к коду " + qr_id, uid, call.message.message_id)
elif data in ["hub_vid", "hub_tst"]:
    users[uid]['current_flow'] = "vid" if data == "hub_vid" else "tst"
    k = InlineKeyboardMarkup(row_width=2)
    cats = ["День рождения", "Свадьба", "Годовщина", "Рождение ребенка", "Свидание", "День влюбленных", "Новый год", "Девичник", "8 Марта", "Коллеге"]
    for c in cats:
        k.insert(Btn(c, callback_data="cat_ok"))
    bot.edit_message_text("Выберите категорию:", uid, call.message.message_id, reply_markup=k)
elif data == "cat_ok":
    k = InlineKeyboardMarkup(row_width=2)
    targs = ["Ему", "Ей", "Семейная пара", "Группа мужчин", "Группа Женщин", "Женщины и Мужчины"]
    for t in targs:
        k.insert(Btn(t, callback_data="targ_ok"))
    bot.edit_message_text("Для кого это?", uid, call.message.message_id, reply_markup=k)
elif data == "targ_ok":
    k = InlineKeyboardMarkup(row_width=2)
    k.add(Btn("0+", callback_data="age_0"), Btn("18+", callback_data="age_18"))
    bot.edit_message_text("Возрастное ограничение:", uid, call.message.message_id, reply_markup=k)
elif data.startswith("age_"):
    flow = users[uid].get('current_flow')
    k = InlineKeyboardMarkup(row_width=1) 
    if flow == "vid":
        k.add(Btn("Видео 1", callback_data="set_vid_1"), Btn("Видео 2", callback_data="set_vid_2"), Btn("Видео 3", callback_data="set_vid_3"))
        bot.edit_message_text("Выберите видео:", uid, call.message.message_id, reply_markup=k)  
    elif flow == "tst":
        for i in range(1, 11):
            k.insert(Btn("Тост " + str(i), callback_data="set_tst_" + str(i)))
        k.add(Btn("🔙 Готово", callback_data="tst_done"))
        bot.edit_message_text("Выберите до 5 тостов. Выбрано: " + str(len(users[uid]['tst'])) + "/5", uid, call.message.message_id, reply_markup=k)
elif data == "hub_gam":
    users[uid]['current_flow'] = "gam"
    k = InlineKeyboardMarkup(row_width=2)
    k.add(Btn("0+", callback_data="age_0_gam"), Btn("18+", callback_data="age_18_gam"))
    bot.edit_message_text("Возрастное ограничение для игры:", uid, call.message.message_id, reply_markup=k)
elif data.startswith("age_0_") or data.startswith("age_18_"):
    k = InlineKeyboardMarkup(row_width=1)
    k.add(Btn("Игра 1", callback_data="set_gam_1"), Btn("Игра 2", callback_data="set_gam_2"), Btn("Игра 3", callback_data="set_gam_3"))
    bot.edit_message_text("Выберите игру:", uid, call.message.message_id, reply_markup=k)
elif data.startswith("set_vid_"):
    users[uid]['vid'] = data.split('_')[2]
    bot.edit_message_text("Видео прикреплено!", uid, call.message.message_id, reply_markup=get_hub_menu(uid)) 
elif data.startswith("set_gam_"):
    users[uid]['gam'] = data.split('_')[2]
    bot.edit_message_text("Игра прикреплена!", uid, call.message.message_id, reply_markup=get_hub_menu(uid))
elif data.startswith("set_tst_"):
    tst_id = data.split('_')[2]
    if len(users[uid]['tst']) < 5 and tst_id not in users[uid]['tst']:
        users[uid]['tst'].append(tst_id)
    k = call.message.reply_markup
    bot.edit_message_text("Выберите до 5 тостов. Выбрано: " + str(len(users[uid]['tst'])) + "/5", uid, call.message.message_id, reply_markup=k)
elif data == "tst_done":
    bot.edit_message_text("Тосты прикреплены!", uid, call.message.message_id, reply_markup=get_hub_menu(uid))
bot.answer_callback_query(call.id)
if name == 'main':
app.run(host='0.0.0.0', port=5000)
