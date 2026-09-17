import telebot
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton as Btn
from flask import Flask, request, redirect, render_template_string, send_from_directory
import json
import os

API_TOKEN = '8808815647:AAF7Bvhh0QEv1HPhIfjAu-WSyrVeB6j_FvA'
bot = telebot.TeleBot(API_TOKEN, threaded=False)
app = Flask(__name__)

DB_FILE = 'database.json'

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_db()
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
        'select_toast': 'Izaberite zdravice:',
        'select_game': 'Izaberite igru:',
        'video_done': 'Video je uspešno dodat!',
        'game_done': 'Igra je uspešno dodata!',
        'tst_done': 'Zdravice su uspešno dodate!',
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
        'select_toast': 'Select toasts:',
        'select_game': 'Select game:',
        'video_done': 'Video attached successfully!',
        'game_done': 'Game attached successfully!',
        'tst_done': 'Toasts attached successfully!',
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
        'select_toast': 'Выберите тосты:',
        'select_game': 'Выберите игру:',
        'video_done': 'Видео успешно прикреплено!',
        'game_done': 'Игра успешно прикреплена!',
        'tst_done': 'Тосты успешно прикреплены!',
        'cats': ["День рождения", "Свадьба", "Годовщина", "Рождение ребенка", "Свидание", "День влюбленных", "Новый год", "Девичник", "8 Марта", "Коллеге"],
        'targs': ["Ему", "Ей", "Семейная пара", "Группа мужчин", "Группа Женщин", "Женщины и Мужчины"]
    }
}

AR_HTML = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">
    <title>Magic AR</title>
    <script src="https://aframe.io/releases/1.3.0/aframe.min.js"></script>
    <script src="https://raw.githack.com/AR-js-org/AR.js/3.3.3/aframe/build/aframe-ar.js"></script>
    <style>
      body { margin: 0; overflow: hidden; background-color: #000; }
      #overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.85); color: white;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        z-index: 9999; font-family: sans-serif; text-align: center; padding: 20px;
      }
      button {
        padding: 15px 40px; font-size: 22px; background: #28a745;
        color: white; border: none; border-radius: 12px; cursor: pointer; margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
      }
      .info { margin-top: 20px; font-size: 14px; color: #aaa; }
    </style>
  </head>
  <body>
    
    <div id="overlay">
      <h2>{{ lang_start }}</h2>
      <button onclick="startAR()">▶ PLAY AR</button>
      <div class="info">{{ info_text }}</div>
    </div>

    <!-- Настройки AR.js для распознавания маркеров -->
    <a-scene embedded arjs="sourceType: webcam; debugUIEnabled: false; trackingMethod: best;" vr-mode-ui="enabled: false">
      <a-assets>
        <video id="ar-video" style="display: none;" src="{{ video_url }}" playsinline webkit-playsinline loop preload="auto"></video>
      </a-assets>

      <!-- ПРИВЯЗКА К МАРКЕРУ -->
      <!-- preset="hiro" означает, что AR будет искать стандартный маркер Hiro -->
      <a-marker preset="hiro">
         <!-- rotation="-90 0 0" кладет видео плашмя на маркер -->
         <!-- position="0 0.1 0" немного приподнимает видео над маркером, чтобы текстуры не сливались -->
         <a-video src="#ar-video" width="1.6" height="0.9" position="0 0.1 0" rotation="-90 0 0"></a-video>
      </a-marker>

      <!-- Камера теперь свободна и снимает окружение -->
      <a-entity camera></a-entity>
    </a-scene>

    <script>
      function startAR() {
        document.getElementById('overlay').style.display = 'none';
        var vid = document.getElementById('ar-video');
        vid.play().catch(function(e) {
          console.log("Autoplay error, trying muted:", e);
          vid.muted = true;
          vid.play();
        });
      }
    </script>
  </body>
</html>
"""



@app.route('/')
@app.route('/<path:subpath>')
def home(subpath=""):
    if subpath.startswith('static/'):
        filename = subpath.replace('static/', '', 1)
        return send_from_directory('static', filename)

    q = request.args.get('id')
    if not q and subpath:
        subpath = subpath.lstrip('/')
        if subpath.startswith('id='):
            q = subpath.split('=')[1]
        elif not subpath.startswith('static/'):
            q = subpath

    if not q:
        return "Scan QR code please."
    
    if q not in db:
        return redirect("https://t.me/my_magic_ar_bot?start=" + str(q))
    
    d = db[q]
    
    vid_id = str(d.get('vid', '1'))
    # Извлекаем только цифру из строки "Видео 1"
    if "1" in vid_id: vid_num = "1"
    elif "2" in vid_id: vid_num = "2"
    elif "3" in vid_id: vid_num = "3"
    else: vid_num = "1"
    
    video_url = f"/static/video{vid_num}.mp4" 

    lang = d.get('lang', 'ru')
    if lang == 'en':
        lang_start = "Experience Magic AR!"
        info_text = f"Selected Video: {vid_id} | Toasts: {len(d.get('tst', []))} | Game: {d.get('gam')}"
    elif lang == 'cr':
        lang_start = "Doživite Magic AR!"
        info_text = f"Odabrano Video: {vid_id} | Zdravice: {len(d.get('tst', []))} | Igra: {d.get('gam')}"
    else:
        lang_start = "Погрузитесь в Magic AR!"
        info_text = f"Видео: {vid_id} | Тостов: {len(d.get('tst', []))} | Игра: {d.get('gam')}"

    return render_template_string(AR_HTML, lang_start=lang_start, info_text=info_text, video_url=video_url)

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
        save_db(db)
        del users[uid]
        bot.edit_message_text(t['done_msg'] + qr_id, uid, call.message.message_id)
        
    elif data == "hub_vid" or data == "hub_tst":
        users[uid]['current_flow'] = "vid" if data == "hub_vid" else "tst"
        k = InlineKeyboardMarkup(row_width=2)
        buttons = [Btn(c, callback_data="cat_ok") for c in t['cats']]
        k.add(*buttons)
        bot.edit_message_text(t['select_cat'], uid, call.message.message_id, reply_markup=k)
        
    elif data == "hub_gam":
        users[uid]['current_flow'] = "gam"
        k = InlineKeyboardMarkup(row_width=2)
        k.add(Btn("0+", callback_data="age_0"), Btn("18+", callback_data="age_18"))
        bot.edit_message_text(t['select_age'], uid, call.message.message_id, reply_markup=k)
        
    elif data == "cat_ok":
        k = InlineKeyboardMarkup(row_width=2)
        buttons = [Btn(tr, callback_data="targ_ok") for tr in t['targs']]
        k.add(*buttons)
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
            t_buttons = [Btn(f"Тост {i}", callback_data=f"set_tst_{i}") for i in range(1, 6)]
            k.add(*t_buttons)
            k.add(Btn("🔙", callback_data="tst_done"))
            bot.edit_message_text(t['select_toast'], uid, call.message.message_id, reply_markup=k)
        elif flow == "gam":
            k.add(
                Btn("Игра 1", callback_data="set_gam_1"),
                Btn("Игра 2", callback_data="set_gam_2"),
                Btn("Игра 3", callback_data="set_gam_3")
            )
            bot.edit_message_text(t['select_game'], uid, call.message.message_id, reply_markup=k)
            
    elif data.startswith("set_vid_"):
        users[uid]['vid'] = data.split('_')[2]
        bot.edit_message_text(t['video_done'], uid, call.message.message_id, reply_markup=get_hub_menu(uid))
        
    elif data.startswith("set_gam_"):
        users[uid]['gam'] = data.split('_')[2]
        bot.edit_message_text(t['game_done'], uid, call.message.message_id, reply_markup=get_hub_menu(uid))
        
    elif data.startswith("set_tst_"):
        tst_id = data.split('_')[2]
        if len(users[uid]['tst']) < 5 and tst_id not in users[uid]['tst']:
            users[uid]['tst'].append(tst_id)
        bot.answer_callback_query(call.id, f"{len(users[uid]['tst'])} / 5")
        return
        
    elif data == "tst_done":
        bot.edit_message_text(t['tst_done'], uid, call.message.message_id, reply_markup=get_hub_menu(uid))

    bot.answer_callback_query(call.id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
