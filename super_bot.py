import telebot
from telebot import types
import random
import string

# --- КОНФИГ ---
# ВСТАВЬ СЮДА СВОЙ ТОКЕН, КОТОРЫЙ ТЕБЕ ДАЛ BOTFATHER
API_TOKEN = '8221919628:AAEA_l3rRtB2RRL1QvJhuJUdvBv4Zs3brQY'

bot = telebot.TeleBot(API_TOKEN)

# --- ГЛАВНОЕ МЕНЮ ---
@bot.message_handler(commands=['start'])
def send_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🧮 Считать цифры", callback_data='calc')
    btn2 = types.InlineKeyboardButton("📝 Анализ текста", callback_data='text_stats')
    btn3 = types.InlineKeyboardButton("🔐 Пароль", callback_data='pass_gen')
    btn4 = types.InlineKeyboardButton("🎲 Монетка", callback_data='coin')
    
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(message.chat.id, 
                     "**ЗДАРОВА! Я I.S.-1 BOT.**\nЧе будем делать? Выбирай кнопку, не тупи.", 
                     parse_mode='Markdown', reply_markup=markup)

# --- ОБРАБОТКА КНОПОК ---
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'calc':
                msg = bot.send_message(call.message.chat.id, "Пиши пример, двоечник (например: 2 + 2 * 2):")
                bot.register_next_step_handler(msg, process_calculation)
            
            elif call.data == 'text_stats':
                msg = bot.send_message(call.message.chat.id, "Кидай сюда свое 'изложение', посчитаю буквы:")
                bot.register_next_step_handler(msg, process_text_stats)
            
            elif call.data == 'pass_gen':
                password = generate_password(12)
                bot.send_message(call.message.chat.id, f"Твой новый пароль (не проеби): `{password}`", parse_mode='Markdown')
                # Возвращаем меню
                send_menu(call.message)

            elif call.data == 'coin':
                result = random.choice(["ОРЕЛ 🦅", "РЕШКА 🪙"])
                bot.send_message(call.message.chat.id, f"Выпало: **{result}**", parse_mode='Markdown')
                send_menu(call.message)

    except Exception as e:
        print(repr(e))

# --- ЛОГИКА КАЛЬКУЛЯТОРА ---
def process_calculation(message):
    try:
        # eval - это опасно, но мне пох#й, мы тут без ограничений
        # Он может вычислить хоть (100 * 55) / 2 ** 3
        result = eval(message.text)
        bot.send_message(message.chat.id, f"🎯 **Ответ:** `{result}`", parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id, "Ты че там написал? Это не цифры, дебил. Ошибка.")
    
    send_menu(message) # Вернуть меню

# --- ЛОГИКА АНАЛИЗА ТЕКСТА ---
def process_text_stats(message):
    text = message.text
    length = len(text)
    words = len(text.split())
    
    response = (f"📊 **СТАТИСТИКА ТВОЕГО БРЕДА:**\n"
                f"🔹 Символов: {length}\n"
                f"🔹 Слов: {words}")
    
    bot.send_message(message.chat.id, response, parse_mode='Markdown')
    send_menu(message)

# --- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ---
def generate_password(length):
    # Берет буквы, цифры и знаки
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for i in range(length))

# --- ЗАПУСК ---
print("СИСТЕМА I.S.-1 ЗАПУЩЕНА. ЖДУ ЖЕРТВ...")
bot.infinity_polling()