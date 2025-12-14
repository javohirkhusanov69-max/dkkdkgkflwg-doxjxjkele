import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import datetime
import random

TOKEN = "8020608436:AAGJKvBxPxMIM_Cw9_mlfbP3hII9_f_ICh0"
FIREBASE_URL = "https://giper-8fd92-default-rtdb.firebaseio.com/users_balance"

bot = telebot.TeleBot(TOKEN)

allowed_prefixes = ["141","129","149"]
allowed_lengths = [10,11,12,13]
user_data = {}  # foydalanuvchi vaqtinchalik ma'lumot saqlash

# /start handler
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("1xBet", callback_data="1xbet"))
    markup.add(InlineKeyboardButton("Melbet", callback_data="melbet"))
    bot.send_message(message.chat.id, f"Hello {message.from_user.first_name} 👋", reply_markup=markup)

# Inline tugma callback
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    platform = call.data
    user_data[user_id] = {"platform": platform}

    if platform == "1xbet":
        text = "🇺🇿 1XBET ID raqamingizni kiriting..."
    else:
        text = "🇺🇿 Melbet ID raqamingizni kiriting..."
    bot.send_message(call.message.chat.id, text)

# ID va summa handler
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text.strip()

    # Agar foydalanuvchi platformani tanlamagan bo'lsa
    if user_id not in user_data or "platform" not in user_data[user_id]:
        bot.send_message(message.chat.id, "❌ Iltimos, /start tugmasi orqali platformani tanlang.")
        return

    # Agar ID hali kiritilmagan bo'lsa
    if "id" not in user_data[user_id]:
        if not text.isdigit() or len(text) not in allowed_lengths or text[:3] not in allowed_prefixes:
            bot.send_message(message.chat.id, "❌ Noto'g'ri ID. Iltimos, tekshirib qayta kiriting.")
            return
        user_data[user_id]["id"] = text
        bot.send_message(message.chat.id, "⬇️Minimal summa 5000 so`m\n⬆️Maksimal summa 40000000 so`m\n\nSummani kiriting...")
        return

    # Agar ID allaqachon kiritilgan bo'lsa, summa qabul qilinadi
    try:
        amount = int(text)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Iltimos, faqat raqam kiriting.")
        return

    if amount < 5000 or amount > 40000000:
        bot.send_message(message.chat.id, "❌ Summa cheklovdan tashqarida.")
        return

    user_balance_id = user_data[user_id]["id"]
    platform = user_data[user_id]["platform"]

    # Firebase ga PUT qilish
    requests.put(f"{FIREBASE_URL}/{user_balance_id}.json", json=amount)

    # Random 5 xonali raqam
    order_id = random.randint(10000, 99999)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    msg = (
        f"✳️ Sizning almashuv buyurtmangiz:\n"
        f"🆔: {order_id}\n"
        f"📤 Berish: {amount} UZS\n"
        f"🇺🇿 tanlangan kantora {platform} ID: {user_balance_id}\n"
        f"📅 Sana: {now}\n\n"
        "Sizning ushbu buyurtmangiz bajarildi! ✅"
    )

    bot.send_message(message.chat.id, msg)
    user_data.pop(user_id, None)  # vaqtinchalik ma'lumotni tozalash

# Botni ishga tushurish
bot.polling(none_stop=True)
