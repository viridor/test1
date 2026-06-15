import os
import telebot
from flask import Flask, request

# קבלת אסימון הבוט (Token) שקיבלת מ-BotFather
# נגדיר אותו בהמשך כמשתנה סביבה (Environment Variable) ב-Render
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Render מספקת באופן אוטומטי את כתובת השרת החיצונית במשתנה הסביבה הזה
RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL')

# אתחול הבוט ושרת ה-Flask
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# נתיב ראשי לבדיקה שהשרת באוויר
@app.route('/')
def index():
    return "הבוט פעיל ומחכה להודעות!", 200

# נתיב ה-Webhook אליו טלגרם תשלח את ההודעות
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Forbidden', 403

# פונקציית הטיפול בהודעות טקסט - הפיכת הטקסט ושליחתו בחזרה
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    original_text = message.text
    # הפיכת הטקסט (תומך בעברית, אנגלית ומספרים בצורה נכונה)
    reversed_text = original_text[::-1]
    bot.reply_to(message, reversed_text)

# נקודת הכניסה של האפליקציה
if __name__ == "__main__":
    # הגדרת ה-Webhook מול השרתים של טלגרם באופן אוטומטי בעליית השרת
    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        print(f"ה-Webhook הוגדר בהצלחה לכתובת: {webhook_url}")
    else:
        print("אזהרה: לא נמצא משתנה סביבה RENDER_EXTERNAL_URL. הגדרת ה-Webhook נכשלה.")

    # הרצת השרת על הפורט ש-Render מקצה דינמית (בדרך כלל 10000)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
