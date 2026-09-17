import telebot
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton as Btn
from flask import Flask, request, redirect

API_TOKEN = '8808815647:AAF7Bvhh0QEv1HPhIfjAu-WSyrVeB6j_FvA'
bot = telebot.TeleBot(API_TOKEN, threaded=False)
app = Flask(__name__)

db = {}
users = {}

LANGS = {
    'cr': {
        'btn_vid': '🎥 Dodaj video',
        'btn_tst': '🥂 Dodaj zdravice',
        'btn_gam': '🎮 Dodaj igru',
        'btn_done': '✅ Potvrdi',
        'btn_reset': '🔄 Počni iznova',
        'done_msg': '🎉 Gotovo! Sve je povezano sa kodom ',
        'select_cat': 'Odaberite kategoriju:',
        'select_targ': 'Za koga je ovo?',
        'select_age': 'Starosno ograničenje:',
        'select_video': 'Izaberite video:',
        'video_done': 'Video je uspešno dodat!',
        'cats': ["Rođendan", "Vjenčanje", "Godišnjica", "Rođenje djeteta", "Sastanak", "Dan zaljubljenih", "Nova godina", "Djevojačko veče", "8. Mart", "Kolegi"],
        'targs': ["Njemu", "Njoj", "Bračni par", "Grupa muškaraca", "Grupa žena", "Žene i muškarci"]
    },
    'en': {
        'btn_vid': '🎥 Attach video',
        'btn_tst': '🥂 Attach toasts',
        'btn_gam': '🎮 Attach game',
        'btn_done': '✅ Confirm',
        'btn_reset': '🔄 Start over',
        'done_msg': '🎉 Done! Everything is linked to code ',
        'select_cat': 'Select category:',
        'select_targ': 'Who is this for?',
        'select_age': 'Age restriction:',
        'select_video': 'Select video:',
        'video_done': 'Video attached successfully!',
        'cats': ["Birthday", "Wedding", "Anniversary", "Newborn", "Date", "Valentine's Day", "New Year", "Bachelorette", "March 8", "Colleague"],
        'targs': ["Him", "Her", "Couple", "Men group", "Women group", "Men & Women"]
    },
    'ru': {
        'btn_vid': '🎥 Прикрепить видео',
        'btn_tst': '🥂 Прикрепить тосты',
        'btn_gam': '🎮 Прикрепить игру',
        'btn_done': '✅ Подтвердить',
        'btn_reset': '🔄 Начать сначала',
        'done_msg': '🎉 Готово! Всё привязано к коду ',
        'select_cat': 'Выберите категорию:',
        'select_targ': 'Для кого это?',
        'select_age': 'Возрастное ограничение:',
        'select_video': 'Выберите видео:',
        'video_done': 'Видео успешно прикреплено!',
        'cats': ["День рождения", "Свадьба", "Годовщина", "Рождение ребенка", "Свидание", "День влюбленных", "Новый год", "Девичник", "8 Марта", "Коллеге"],
        'targs': ["Ему", "Ей", "Семейная пара", "Группа мужчин", "Группа Женщин", "Женщины и Мужчины"]
    }
}

@app.route('/')
@app.route('/<path:subpath>')
def home(subpath=""):
    q = request.args.get('id')
    if not q and subpath:
        subpath = subpath.lstrip('/')
        if subpath.startswith('id='):
            q = subpath.split('=')[1]
        else:
            q = subpath

    if not q:
        return "Scan QR code please."
    if q not in db:
        return redirect("https://t.me/my_magic_ar_bot?start=" + str(q))
    
    d = db[q]
    res = []
    res.append("<h1>AR (" + str(d.get('lang', 'ru')) + ")</h1><br>")
    if d.get('vid'):
        res.append("Video: " + str(d.get('vid')) + "<br>")
    if d.get('tst'):
        res.append("Toasts: " + ", ".join(d.get('tst', [])) + "<br>")
    if d.get('gam'):
        res.append("Game: " + str(d.get('gam')) + "<br>")
    return "".join(res)

@app.route('/webhook', methods=['POST'])
def webhook():
    raw_data = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(raw_data)
    bot.process_new_updates([update])
    return "OK", 200

def get_hub_menu(uid):
    if uid not in users:
        users[uid] = {'qr': 'box777', 'lang': 'ru', 'vid': None, 'tst': [], 'gam': None}
    lang_code = users[uid].get('lang', 'ru')
    t = LANGS.get(lang_code, LANGS['ru'])
    k = InlineKeyboardMarkup(row_width=1)
    
    if not users[uid].get('vid'):
        k.add(Btn(t['btn_vid'], callback_data="hub_vid"))
    if not users[uid].get('tst'):
        k.add(Btn(t['btn_tst'], callback_data="hub_tst"))
    if not users[uid].get('gam'):
        k.add(Btn(t['btn_gam'], callback_data="hub_gam"))
        
    if users[uid].get('vid') or users[uid].get('tst') or users[uid].get('gam'):
        k.add(Btn(t['btn_done'], callback_data="hub_done"))
        k.add(Btn(t['btn_reset'], callback_data="hub_reset"))
    return k

@bot.message_handler(commands=['start'])
def start_command(message):
    uid = message.chat.id
    text = message.text.split()
    qr_id = text[1] if len(text) > 1 else "box777"
    users[uid] = {'qr': qr_id, 'lang': None, 'vid': None, 'tst': [], 'gam': None}
    
    k = InlineKeyboardMarkup(row_width=1)
    k.add(
        Btn("🇲🇪 Crnogorski", callback_data="lang_cr"),
        Btn("🇬🇧 English", callback_data="lang_en"),
        Btn("🇷🇺 Русский", callback_data="lang_ru")
    )
    bot.send_message(uid, "Izaberite jezik / Choose language / Выберите язык:", reply_markup=k)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    uid = call.message.chat.id
    data = call.data
    if uid not in users:
        users[uid] = {'qr': 'box777', 'lang': 'ru', 'vid': None, 'tst': [], 'gam': None}

    lang_code = users[uid].get('lang', 'ru')
    t = LANGS.get(lang_code, LANGS['ru'])

    if data.startswith("lang_"):
        selected_lang = data.split('_')[1]
        users[uid]['lang'] = selected_lang
        t_new = LANGS[selected_lang]
        bot.edit_message_text(t_new['btn_vid'].split()[1] + " / Menu:", uid, call.message.message_id, reply_markup=get_hub_menu(uid))
        
    elif data == "hub_reset":
        qr_id = users[uid]['qr']
        users[uid] = {'qr': qr_id, 'lang': None, 'vid': None, 'tst': [], 'gam': None}
        k = InlineKeyboardMarkup(row_width=1)
        k.add(
            Btn("🇲🇪 Crnogorski", callback_data="lang_cr"),
            Btn("🇬🇧 English", callback_data="lang_en"),
            Btn("🇷🇺 Русский", callback_data="lang_ru")
        )
        bot.edit_message_text("Izaberite jezik / Choose language / Выберите язык:", uid, call.message.message_id, reply_markup=k)
        
    elif data == "hub_done":
        qr_id = users[uid]['qr']
        db[qr_id] = users[uid]
        del users[uid]
        bot.edit_message_text(t['done_msg'] + qr_id, uid, call.message.message_id)
        
    elif data == "hub_vid" or data == "hub_tst":
        users[uid]['current_flow'] = "vid" if data == "hub_vid" else "tst"
        k = InlineKeyboardMarkup(row_width=2)
        for c in t['cats']:
            k.insert(Btn(c, callback_data="cat_ok"))
        bot.edit_message_text(t['select_cat'], uid, call.message.message_id, reply_markup=k)
        
    elif data == "hub_gam":
        users[uid]['current_flow'] = "gam"
        k = InlineKeyboardMarkup(row_width=2)
        k.add(Btn("0+", callback_data="age_0_gam"), Btn("18+", callback_data="age_18_gam"))
        bot.edit_message_text(t['select_age'], uid, call.message.message_id, reply_markup=k)
        
    elif data == "cat_ok":
        k = InlineKeyboardMarkup(row_width=2)
        for tr in t['targs']:
            k.insert(Btn(tr, callback_data="targ_ok"))
        bot.edit_message_text(t['select_targ'], uid, call.message.message_id, reply_markup=k)
        
    elif data == "targ_ok":
        k = InlineKeyboardMarkup(row_width=2)
        k.add(Btn("0+", callback_data="age_0"), Btn("18+", callback_data="age_18"))
        bot.edit_message_text(t['select_age'], uid, call.message.message_id, reply_markup=k)
        
    elif data.startswith("age_"):
        flow = users[uid].get('current_flow')
        k = InlineKeyboardMarkup(row_width=1)
        if flow == "vid":
            k.add(
                Btn("Видео 1", callback_data="set_vid_1"),
                Btn("Видео 2", callback_data="set_vid_2"),
                Btn("Видео 3", callback_data="set_vid_3")
            )
            bot.edit_message_text(t['select_video'], uid, call.message.message_id, reply_markup=k)
        elif flow == "tst":
            for i in range(1, 6):
                k.insert(Btn(f"Тост {i}", callback_data=f"set_tst_{i}"))
            k.add(Btn("🔙 Готово", callback_data="tst_done"))
            bot.edit_message_text("Выберите тосты:", uid, call.message.message_id, reply_markup=k)
            
    elif data.startswith("age_0_") or data.startswith("age_18_"):
        k = InlineKeyboardMarkup(row_width=1)
        k.add(Btn("Игра 1", callback_data="set_gam_1"), Btn("Игра 2", callback_data="set_gam_2"))
        bot.edit_message_text("Выберите игру:", uid, call.message.message_id, reply_markup=k)
        
    elif data.startswith("set_vid_"):
        users[uid]['vid'] = data.split('_')[2]
        bot.edit_message_text(t['video_done'], uid, call.message.message_id, reply_markup=get_hub_menu(uid))
        
    elif data.startswith("set_gam_"):
        users[uid]['gam'] = data.split('_')[2]
        bot.edit_message_text("Игра прикреплена!", uid, call.message.message_id, reply_markup=get_hub_menu(uid))
        
    elif data.startswith("set_tst_"):
        tst_id = data.split('_')[2]
        if len(users[uid]['tst']) < 5 and tst_id not in users[uid]['tst']:
            users[uid]['tst'].append(tst_id)
        bot.answer_callback_query(call.id, f"Выбрано тостов: {len(users[uid]['tst'])}")
        return
        
    elif data == "tst_done":
        bot.edit_message_text("Тосты прикреплены!", uid, call.message.message_id, reply_markup=get_hub_menu(uid))

    bot.answer_callback_query(call.id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
