import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import requests

API_TOKEN = "8585059102:AAE491JdeudjOMZcJ3Myd1X6GpVOp3zXEAA"
ADMIN_ID = 7894314746

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_phone = {}
user_active = {}
user_enter_id = {}

def make_grid(ap):
    rows = len(ap)
    cols = len(ap[0])
    out = ""
    for r in range(rows):
        for c in range(cols):
            out += "🍏" if ap[r][c] == 1 else "🍎"
        out += "\n"
    return out


@dp.message_handler(commands=["start"])
async def start_cmd(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("📱 Raqam ulashish", request_contact=True))
    await msg.answer("Raqamingizni ulashing:", reply_markup=kb)


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def get_contact(msg: types.Message):
    phone = msg.contact.phone_number
    user_phone[msg.from_user.id] = phone

    txt = f"Yangi foydalanuvchi:\nUsername: @{msg.from_user.username}\nRaqam: {phone}"
    kb = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("Activate", callback_data=f"activate_{msg.from_user.id}"),
        types.InlineKeyboardButton("Admin", url="https://t.me/bytrox_1")
    )
    await bot.send_message(ADMIN_ID, txt, reply_markup=kb)

    await msg.answer(
        f"👋 hello {msg.from_user.first_name}\nPlease active your account message to admin",
        reply_markup=types.ReplyKeyboardRemove()
    )


@dp.callback_query_handler(lambda c: c.data.startswith("activate_"))
async def activate_user(call: types.CallbackQuery):
    uid = int(call.data.split("_")[1])
    user_active[uid] = True

    await bot.send_message(uid, "Your activated")

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("GET SIGNAL")
    await bot.send_message(uid, "GET SIGNAL tugmasidan foydalaning", reply_markup=kb)

    await call.answer("Activated")


@dp.message_handler(lambda m: m.text == "GET SIGNAL")
async def get_signal(msg: types.Message):
    uid = msg.from_user.id

    if not user_active.get(uid):
        return await msg.answer("You not activated.")

    if uid not in user_enter_id:
        user_enter_id[uid] = None
        return await msg.answer("Enter your id:")

    user_id_value = user_enter_id[uid]

    data = {
        "user_id": user_id_value,
        "otp_code": "BYTROX-VIP-3RYICW-MNA21N-07Y",
        "key": "ran"
    }

    r = requests.post("https://bytrox.shop/apple/data.php", json=data)
    js = r.json()

    if "AP" not in js:
        return await msg.answer("Buy from admin")

    ap = js["AP"]
    grid = make_grid(ap)

    await msg.answer(grid)


@dp.message_handler()
async def get_user_id(msg: types.Message):
    uid = msg.from_user.id

    if uid in user_enter_id and user_enter_id[uid] is None:
        user_enter_id[uid] = msg.text
        return await msg.answer("Again GET SIGNAL click")
