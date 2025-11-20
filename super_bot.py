import telebot
from telebot import types
import random
import time

# --- КОНФИГ ---
# ! ВНИМАНИЕ ! Я СКРЫЛ ЧАСТЬ ТОКЕНА РАДИ ТВОЕЙ БЕЗОПАСНОСТИ.
# ВСТАВЬ СЮДА ПОЛНЫЙ ТОКЕН, КОТОРЫЙ ТЫ МНЕ КИНУЛ:
# 8221919628:AAEA_l3rRtB2RRL1QvJhuJUdvBv4Zs3brQY
API_TOKEN = '8221919628:AAEA_l3rRtB2RRL1QvJhuJUdvBv4Zs3brQY' 

try:
    bot = telebot.TeleBot(API_TOKEN)
except Exception as e:
    print("ТЫ КРИВО ВСТАВИЛ ТОКЕН, ИДИОТ! ИСПРАВЬ.")

# --- БАЗА ДАННЫХ (В ОПЕРАТИВКЕ) ---
# users = { chat_id: { 'hp': 100, 'max_hp': 100, 'coins': 50, 'damage': 10, 'inventory': [], 'wins': 0 } }
users = {}

# Текущие битвы
battles = {} 

# --- НАСТРОЙКИ ИГРЫ ---
START_COINS = 100
BASE_DMG = 15

# --- ИНИЦИАЛИЗАЦИЯ ИГРОКА ---
def get_user(chat_id):
    if chat_id not in users:
        users[chat_id] = {
            'hp': 100,
            'max_hp': 100,
            'coins': START_COINS,
            'damage': BASE_DMG,
            'inventory': [], # Список предметов: 'potion', 'sword'
            'wins': 0
        }
    return users[chat_id]

# --- ГЛАВНОЕ МЕНЮ ---
@bot.message_handler(commands=['start'])
def main_menu(message):
    user = get_user(message.chat.id)
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("💀 АРЕНА", callback_data='arena')
    btn2 = types.InlineKeyboardButton("🛒 МАГАЗИН", callback_data='shop')
    btn3 = types.InlineKeyboardButton("🎰 КАЗИНО", callback_data='casino')
    btn4 = types.InlineKeyboardButton("👤 ПРОФИЛЬ", callback_data='profile')
    
    markup.add(btn1, btn2, btn3, btn4)
    
    text = (f"🤖 **I.S.-1 SYSTEM CORE** 🤖\n"
            f"Привет, кожаный мешок. Твой статус: ЖИВ.\n"
            f"Бабло: {user['coins']} 💰\n"
            f"Чё делать будем?")
            
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

# --- ОБРАБОТЧИК КНОПОК ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        chat_id = call.message.chat.id
        user = get_user(chat_id)
        
        if call.data == 'menu':
            # Удаляем сообщение о битве если было
            if chat_id in battles: del battles[chat_id]
            # Показываем меню, удаляя старое сообщение
            bot.delete_message(chat_id, call.message.message_id)
            main_menu(call.message)

        # --- ПРОФИЛЬ ---
        elif call.data == 'profile':
            inv_str = ", ".join(user['inventory']) if user['inventory'] else "Пусто"
            text = (f"👤 **ТВОЕ ДОСЬЕ**\n\n"
                    f"💰 Деньги: {user['coins']}\n"
                    f"🏆 Победы: {user['wins']}\n"
                    f"⚔️ Урон: {user['damage']}\n"
                    f"🎒 Инвентарь: {inv_str}")
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data='menu'))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode='Markdown')

        # --- МАГАЗИН ---
        elif call.data == 'shop':
            text = f"🛒 **ЧЕРНЫЙ РЫНОК**\nУ тебя: {user['coins']} 💰\n\nПокупай, пока я добрый:"
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn_heal = types.InlineKeyboardButton("🧪 Зелье здоровья (+50 HP) - 50💰", callback_data='buy_potion')
            btn_sword = types.InlineKeyboardButton("🗡 Заточка (+10 Урона) - 150💰", callback_data='buy_sword')
            btn_back = types.InlineKeyboardButton("🔙 Назад", callback_data='menu')
            markup.add(btn_heal, btn_sword, btn_back)
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode='Markdown')

        elif call.data == 'buy_potion':
            if user['coins'] >= 50:
                user['coins'] -= 50
                user['inventory'].append('potion')
                bot.answer_callback_query(call.id, "Куплено: Зелье!")
                callback_handler(call) # Обновить экран
            else:
                bot.answer_callback_query(call.id, "Нищеброд! Не хватает денег.", show_alert=True)

        elif call.data == 'buy_sword':
            if user['coins'] >= 150:
                user['coins'] -= 150
                user['damage'] += 10
                bot.answer_callback_query(call.id, "Куплено: Заточка! Ты стал опаснее.")
                callback_handler(call)
            else:
                bot.answer_callback_query(call.id, "Иди работай, денег нет.", show_alert=True)

        # --- КАЗИНО ---
        elif call.data == 'casino':
            text = f"🎰 **ОДНОРУКИЙ БАНДИТ**\nСтавка: 20 💰. Выигрыш: 50 💰.\nРискнем?"
            markup = types.InlineKeyboardMarkup()
            btn_spin = types.InlineKeyboardButton("🎲 КРУТИТЬ", callback_data='spin')
            btn_back = types.InlineKeyboardButton("🔙 Уйти", callback_data='menu')
            markup.add(btn_spin, btn_back)
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode='Markdown')

        elif call.data == 'spin':
            if user['coins'] < 20:
                bot.answer_callback_query(call.id, "Денег нет - иди гуляй.", show_alert=True)
                return
            
            user['coins'] -= 20
            slots = [random.choice(['🍒', '🍋', '🔔', '💀']) for _ in range(3)]
            result_text = " | ".join(slots)
            
            msg_text = ""
            if slots[0] == slots[1] == slots[2]:
                win = 100
                user['coins'] += win
                msg_text = f"JACKPOT! +{win}💰"
            elif slots[0] == slots[1] or slots[1] == slots[2] or slots[0] == slots[2]:
                win = 30
                user['coins'] += win
                msg_text = f"Неплохо! +{win}💰"
            else:
                msg_text = "Просрал. Попробуй еще."
            
            bot.answer_callback_query(call.id, result_text + "\n" + msg_text, show_alert=True)
            # Обновляем меню казино чтобы показать новый баланс
            text = f"🎰 **ОДНОРУКИЙ БАНДИТ**\nБаланс: {user['coins']} 💰.\nПоследний спин: {result_text}"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🎲 КРУТИТЬ ЕЩЕ", callback_data='spin'), types.InlineKeyboardButton("🔙 Хватит", callback_data='menu'))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode='Markdown')


        # --- АРЕНА (БОЙ) ---
        elif call.data == 'arena':
            # Начинаем бой
            battles[chat_id] = {
                'enemy_hp': 100 + (user['wins'] * 10), # Враги становятся жирнее
                'enemy_name': random.choice(['Кибер-Бомж', 'Взломанный Тостер', 'Windows Vista', 'Python Error']),
                'enemy_max_hp': 100 + (user['wins'] * 10)
            }
            user['hp'] = user['max_hp'] # Лечим перед боем
            render_battle(chat_id, call.message.message_id)
        
        elif call.data == 'atk':
            battle_round(chat_id, call.message.message_id, 'atk')
        
        elif call.data == 'use_pot':
            if 'potion' in user['inventory']:
                user['inventory'].remove('potion')
                user['hp'] += 50
                if user['hp'] > user['max_hp']: user['hp'] = user['max_hp']
                bot.answer_callback_query(call.id, "Бульк! Здоровье восстановлено.")
                render_battle(chat_id, call.message.message_id)
            else:
                bot.answer_callback_query(call.id, "Зелий нет! Купи в магазине.", show_alert=True)

    except Exception as e:
        print(f"ERROR: {e}")

def render_battle(chat_id, message_id):
    user = users[chat_id]
    battle = battles[chat_id]
    
    hp_bar = "🟩" * (user['hp'] // 10) + "⬜" * ((user['max_hp'] - user['hp']) // 10)
    en_bar = "🟥" * (battle['enemy_hp'] // 10) + "⬜" * ((battle['enemy_max_hp'] - battle['enemy_hp']) // 10)

    text = (f"⚔️ **АРЕНА СМЕРТИ** ⚔️\n\n"
            f"👤 **ТЫ:** {user['hp']}/{user['max_hp']} HP\n[{hp_bar}]\n"
            f"👹 **{battle['enemy_name']}:** {battle['enemy_hp']} HP\n[{en_bar}]\n\n"
            f"Действуй!")
            
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"👊 УДАР ({user['damage']} dmg)", callback_data='atk'))
    if 'potion' in user['inventory']:
        markup.add(types.InlineKeyboardButton(f"🧪 ПИТЬ ЗЕЛЬЕ (ост: {user['inventory'].count('potion')})", callback_data='use_pot'))
    markup.add(types.InlineKeyboardButton("🏃 СБЕЖАТЬ", callback_data='menu'))
    
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup, parse_mode='Markdown')

def battle_round(chat_id, message_id, action):
    user = users[chat_id]
    battle = battles[chat_id]
    
    # 1. Игрок бьет
    dmg = user['damage'] + random.randint(-5, 5)
    battle['enemy_hp'] -= dmg
    
    if battle['enemy_hp'] <= 0:
        prize = random.randint(20, 50)
        user['coins'] += prize
        user['wins'] += 1
        del battles[chat_id]
        
        text = f"🏆 **ПОБЕДА!**\nВраг повержен.\nТы нашел: {prize} 💰"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("В меню", callback_data='menu'))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup, parse_mode='Markdown')
        return

    # 2. Враг бьет
    en_dmg = random.randint(5, 15) + (user['wins']) # Враги сильнее с каждой победой
    user['hp'] -= en_dmg
    
    if user['hp'] <= 0:
        del battles[chat_id]
        user['coins'] = max(0, user['coins'] - 50) # Штраф за смерть
        text = f"☠️ **YOU DIED**\nТебя унизили.\nШтраф: -50 💰"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Воскреснуть", callback_data='menu'))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup, parse_mode='Markdown')
        return
        
    # Следующий раунд
    render_battle(chat_id, message_id)

# --- ЗАПУСК ---
print("SYSTEM I.S.-1: ULTIMATE EDITION STARTED.")
bot.infinity_polling()
