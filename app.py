from flask import Flask, request, redirect

app = Flask(__name__)

# Временная тестовая база данных
db = {}

@app.route('/')
def home():
    qr_id = request.args.get('id')
    
    if not qr_id:
        return "Пожалуйста, отсканируйте QR-код."
        
    if qr_id not in db:
        bot_link = "https://t.me/my_magic_ar_bot?start=" + str(qr_id)
        return redirect(bot_link)
        
    return "Здесь будет открываться дополненная реальность (AR)!"
