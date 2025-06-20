import telebot
import time
from telebot import types
from datetime import datetime

TOKEN = "7831635287:AAHqOjx0I2MfTqpDkNgijMoJB3MoHwek-Dg"
ADMIN_ID = 1013151555
GROUP_ID = -1002707812587  # Ishchilar hisobotini jo'natish uchun
GROUP_ID2 = -4956700662  # Mahsulotlarni jo'natish uchun
ALLOWED_USERS = [20481, 6694546824, 1649810353, 7689968537, 2049117384, 1013151555]

bot = telebot.TeleBot(TOKEN)

user_sessions = {}

DETSKIY_ISHLAR = [
    "Yelka tikish", "Bayka qo'yish", "Bayka bostirish", "Yoqa qo‘yuvchi", "Overlok", "Bakavoy", "Rezinka raspa", "Dazmol",
    "Upakovka", "Oldi bostiriq", "Yeng qo‘yuvchi", "Yeng raspa",
    "Shortik raspa", "Etak raspa", "Rezinka tayyorlash", "Yoqa tayyorlash",
    "Kantrol", "Rezinka qo'yish", "Chistka", "Dazmol-Upakovka"
]

KATTALAR_ISHLAR = [
    "Beyka kesih", "Yelka tikuvchi", "Yoqa tayyorlovchi", "Yoqa qo‘yuvchi",
    "Beyka qo‘yuvchi", "Beyka Zakrepka", "Beyka bostiruvchi", "Oldi raspachi",
    "Yeng qo‘yuvchi", "Bakavoy tikuvchi", "Yeng raspachi", "Etak raspachi",
    "Razmer", "Chistkachi", "Dazmolchi", "Kontrol", "Upakovka"
]


@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    if ALLOWED_USERS and user_id not in ALLOWED_USERS:
        bot.send_message(user_id, "🚫 Sizda bu botdan foydalanish huquqi yo‘q. Iltimos, rahbariyat bilan bog‘laning."
                                  "👨‍💻 @murodjon_m")
        return

    start_session(user_id)
    send_type_selection(user_id)


def start_session(user_id):
    user_sessions[user_id] = {
        "step": "choose_type",
        "type": "",
        "ishchi": "",
        "ishlar": [],
        "mode": None  # 'worker' yoki 'product'
    }


def send_type_selection(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("👶 DETSKIY futbolka", "👕 KATTALAR futbolka")
    bot.send_message(user_id, "⚙️ Qaysi turdagi futbolkaga hisobot kiritmoqchisiz?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    if call.data == "restart_yes":
        mode = user_sessions.get(user_id, {}).get("mode")
        if mode == "worker":
            user_sessions[user_id]["step"] = "get_worker_name"
            bot.send_message(user_id, "Ishchining ismini kiriting:")
        elif mode == "product":
            user_sessions[user_id]["finished"] = {}  # Eski ma'lumotni o'chir
            if user_sessions[user_id]["type"] == "DETSKIY":
                user_sessions[user_id]["step"] = "get_product_type"
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                markup.add("Futbolka", "Shortik")
                bot.send_message(user_id, "Qaysi mahsulot turi?", reply_markup=markup)
            else:
                user_sessions[user_id]["step"] = "get_color"
                bot.send_message(user_id, "Rangini kiriting:")
        else:
            start_session(user_id)
            send_type_selection(user_id)

    elif call.data == "restart_no":
        bot.send_message(user_id, "🏁 Rahmat! /start buyrug‘i orqali qaytadan boshlashingiz mumkin.")
        user_sessions.pop(user_id, None)


def ask_restart(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Ha", callback_data="restart_yes"),
        types.InlineKeyboardButton("❌ Yo‘q", callback_data="restart_no")
    )
    bot.send_message(user_id, "🔁 Yana hisobot yubormoqchimisiz?", reply_markup=markup)


@bot.message_handler(func=lambda m: True)
def message_handler(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if user_id not in user_sessions:
        bot.send_message(user_id, "Iltimos, /start buyrug‘ini yuboring.")
        return

    session = user_sessions[user_id]

    if session["step"] == "choose_type":
        if "DETSKIY" in text:
            session["type"] = "DETSKIY"
        elif "KATTALAR" in text:
            session["type"] = "KATTALAR"
        else:
            bot.send_message(user_id, "Iltimos, to‘g‘ri tur tanlang.")
            return

        session["step"] = "choose_action"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("🔘 Ishchi ishi haqida hisobot", "🔘 Tayyor futbolkalar (pastga tushganlar)")
        bot.send_message(user_id, "Endi qaysi ma’lumotni kiritmoqchisiz?", reply_markup=markup)

    elif session["step"] == "choose_action":
        if "Ishchi ishi" in text:
            session["step"] = "get_worker_name"
            bot.send_message(user_id, "Ishchining ismini kiriting:")
        elif "Tayyor futbolkalar" in text:
            session["finished"] = {}
            if session["type"] == "DETSKIY":
                session["step"] = "get_product_type"
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                markup.add("Futbolka", "Shortik")
                bot.send_message(user_id, "Qaysi mahsulot turi?", reply_markup=markup)
            else:
                session["step"] = "get_color"
                bot.send_message(user_id, "Rangini kiriting:")

    elif session["step"] == "get_product_type":
        session["finished"]["type"] = text
        session["step"] = "get_age"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("2 yosh", "4 yosh", "6 yosh", "8 yosh")
        bot.send_message(user_id, "Yoshini tanlang:", reply_markup=markup)

    elif session["step"] == "get_age":
        session["finished"]["age"] = text
        session["step"] = "get_color"
        bot.send_message(user_id, "Rangini kiriting:")

    elif session["step"] == "get_color":
        session["finished"]["color"] = text
        session["step"] = "get_finished_data"
        bot.send_message(user_id, "Chistkadan chiqqan mahsulot soni:")

    elif session["step"] == "get_worker_name":
        session["ishchi"] = text
        session["step"] = "select_task"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        task_list = DETSKIY_ISHLAR if session["type"] == "DETSKIY" else KATTALAR_ISHLAR
        for task in task_list:
            markup.add(task)
        bot.send_message(user_id, "Qaysi ishni bajargan?", reply_markup=markup)

    elif session["step"] == "select_task":
        session["current_task"] = text
        session["step"] = "enter_quantity"
        bot.send_message(user_id, f'"{text}" ishidan nechta dona qilgan?')

    elif session["step"] == "enter_quantity":
        try:
            count = int(text)
            session["ishlar"].append((session["current_task"], count))
            session["step"] = "add_more"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add("✅ Yakunlash", "➕ Yana qo‘shish")
            bot.send_message(user_id, "Yana ish qo‘shmoqchimisiz?", reply_markup=markup)
        except:
            bot.send_message(user_id, "Faqat raqam kiriting.")

    elif session["step"] == "add_more":
        if "Yakunlash" in text:
            jami_dona = sum(i[1] for i in session["ishlar"])
            jami_sum = 0
            msg = f"#{session['type']}\n\n"
            msg += f"📅 Sana: {datetime.now().strftime('%Y-%m-%d')}\n"
            msg += f"👤 Kirituvchi: {message.from_user.first_name}"
            if user_id == 2049117384:
                msg += " (texnolog)"
            msg += f"\n👕 Ishchi: {session['ishchi']}\n\n"
            msg += f"🧵 Bajarilgan ishlar:\n"

            for task, amount in session["ishlar"]:
                if session['type'] == "DETSKIY":
                    narx = {
                        "Yelka tikish": 100,
                        "Overlok": 200,
                        "Bayka bostirish": 140,
                        "Bayka qo'yish": 130,
                        "Yoqa qo‘yuvchi": 140,
                        "Bakavoy": 250,
                        "Rezinka raspa": 140,
                        "Dazmol": 150,
                        "Upakovka": 200,
                        "Oldi bostiriq": 100,
                        "Yeng qo‘yuvchi": 200,
                        "Yeng raspa": 120,
                        "Shortik raspa": 180,
                        "Etak raspa": 110,
                        "Rezinka tayyorlash": 70,
                        "Yoqa tayyorlash": 90,
                        "Kantrol": 160,
                        "Rezinka qo'yish": 140,
                        "Chistka": 180,
                        "Dazmol-Upakovka": 200
                    }.get(task, 0)
                else:
                    narx = {
                        "Yelka tikuvchi": 110,
                        "Yoqa tayyorlovchi": 70,
                        "Yoqa qo‘yuvchi": 170,
                        "Beyka qo‘yuvchi": 90,
                        "Beyka Zakrepka": 90,
                        "Beyka bostiruvchi": 130,
                        "Oldi raspachi": 100,
                        "Yeng qo‘yuvchi": 170,
                        "Bakavoy tikuvchi": 250,
                        "Yeng raspachi": 150,
                        "Etak raspachi": 150,
                        "Razmer": 80,
                        "Chistkachi": 180,
                        "Dazmolchi": 150,
                        "Kontrol": 160,
                        "Upakovka": 200,
                    }.get(task, 0)

                summa = amount * narx
                jami_sum += summa
                msg += f" - {task}: {amount} dona × {narx} so‘m = {summa:,} so‘m\n"

            msg += f"\n📦 Umumiy: {jami_dona} dona"
            msg += f"\n💰 Umumiy hisob: {jami_sum:,} so‘m"

            bot.send_message(ADMIN_ID, msg)
            bot.send_message(GROUP_ID, msg)
            bot.send_message(user_id, "✅ Hisobot yuborildi.")
            session["mode"] = "worker"
            ask_restart(user_id)


        else:
            session["step"] = "select_task"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            task_list = DETSKIY_ISHLAR if session["type"] == "DETSKIY" else KATTALAR_ISHLAR
            for task in task_list:
                markup.add(task)
            bot.send_message(user_id, "Yana biror ishni tanlang:", reply_markup=markup)

    elif session["step"] == "get_finished_data":
        try:
            if "chistka" not in session["finished"]:
                session["finished"]["chistka"] = int(text)
                bot.send_message(user_id, "Dazmolga tushgan soni:")
            elif "dazmol" not in session["finished"]:
                session["finished"]["dazmol"] = int(text)
                bot.send_message(user_id, "Upakovka qilingan soni:")
            else:
                session["finished"]["upakovka"] = int(text)
                f = session["finished"]
                msg = f"#{session['type']}\n\n"
                msg += f"📅 Sana: {datetime.now().strftime('%Y-%m-%d')}\n"
                msg += f"👤 Kirituvchi: {message.from_user.first_name}"
                if user_id == 2049117384:
                    msg += " (texnolog)"
                msg += "\n"
                if session["type"] == "DETSKIY":
                    msg += f"\n👕 Mahsulot turi: {f['type']}\n"
                    msg += f"👶 Yosh: {f['age']}\n"
                msg += f"🎨 Rang: {f['color']}\n"
                msg += f"\n📦 Tayyor mahsulotlar:\n"
                msg += f" - Chistkadan chiqqan: {f['chistka']} dona\n"
                msg += f" - Dazmolga tushgan: {f['dazmol']} dona\n"
                msg += f" - Upakovka qilingan: {f['upakovka']} dona"
                bot.send_message(ADMIN_ID, msg)
                bot.send_message(GROUP_ID2, msg)
                bot.send_message(user_id, "✅ Tayyor mahsulotlar hisobot yuborildi.")
                session["mode"] = "product"
                ask_restart(user_id)
        except:
            bot.send_message(user_id, "Iltimos, faqat raqam kiriting.")


def ask_restart(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Ha", callback_data="restart_yes"),
        types.InlineKeyboardButton("❌ Yo‘q", callback_data="restart_no")
    )
    bot.send_message(user_id, "🔁 Yana hisobot yubormoqchimisiz?", reply_markup=markup)


# # ✅ Inline tugma uchun handler
# @bot.callback_query_handler(func=lambda call: True)
# def callback_handler(call):
#     user_id = call.from_user.id
#
#     if call.data == "restart_yes":
#         user_sessions[user_id] = {
#             "step": "choose_type",
#             "type": "",
#             "ishchi": "",
#             "ishlar": []
#         }
#         markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#         markup.add("👶 DETSKIY futbolka", "👕 KATTALAR futbolka")
#         bot.send_message(user_id, "⚙️ Qaysi turdagi futbolkaga hisobot kiritmoqchisiz?", reply_markup=markup)
#
#     elif call.data == "restart_no":
#         bot.send_message(user_id, "🏁 Rahmat! /start buyrug‘i orqali qaytadan boshlashingiz mumkin.")
#         user_sessions.pop(user_id, None)


while True:
    try:
        bot.infinity_polling(timeout=30, long_polling_timeout=20)
    except Exception as e:
        print(f"Xatolik: {e}")
        time.sleep(5)  # 5 soniya kutib qayta ishga tushadi
