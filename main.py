import telebot
from telebot import types
import json

bot = telebot.TeleBot('# TG bot key')

adminID = 1 # adminID
adminID1 = 2 # adminID1

try:
    with open('data.json', 'r') as data_file:
        data = json.load(data_file)
except FileNotFoundError:
    data = {}

data.setdefault('joinedUsers', {})
data.setdefault('usergames', {})

max_players = 8


@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    user_first_name = message.from_user.first_name
    user_username = message.from_user.username

    if user_id not in data['joinedUsers']:
        data['joinedUsers'][user_id] = {"id": user_id, "first_name": user_first_name, "username": f"@{user_username}"}
        save_data()

        admin_message = f"Пользователь {user_first_name} (@{user_username}) присоединился к боту"
        bot.send_message(adminID, admin_message)
        bot.send_message(adminID1, admin_message)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("📅 Расписание")
    item2 = types.KeyboardButton("📝 Чат")
    markup.add(item1, item2)

    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}! Я рад, что вы заинтересовались игрой "
                                      "TTM Board Game. Нажмите на кнопку ниже, чтобы увидеть доступные игры и "
                                      "записаться ⬇", parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['sendall'])
def send_all(message):
    if message.chat.id not in (adminID, adminID1):
        bot.send_message(message.chat.id, 'Error')
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, 'Использование: /sendall текст сообщения')
        return

    bot.send_message(message.chat.id, 'Start')
    for user_id, name in data['joinedUsers'].items():
        bot.send_message(user_id, parts[1])
    bot.send_message(message.chat.id, 'Done')


@bot.message_handler(content_types=['text'])
def games(message):
    if message.chat.type == 'private':
        if message.text == '📅 Расписание':
            markup = types.InlineKeyboardMarkup(row_width=1)
            item1 = types.InlineKeyboardButton("Игра №1", callback_data='game 1')
            markup.add(item1)
            bot.send_message(message.chat.id, 'Доступные игры', reply_markup=markup)
        elif message.text == '📝 Чат':
            markup = types.InlineKeyboardMarkup(row_width=1)
            item2 = types.InlineKeyboardButton("Игра №1", callback_data='game 1')
            markup.add(item2)
            welcome_message = "Заходите в наш [чат](# link to the chat) и узнавайте всю информацию первыми"
            bot.send_message(message.chat.id, welcome_message, parse_mode='Markdown')


def save_data():
    with open('data.json', 'w') as dataFile:
        json.dump(data, dataFile, ensure_ascii=False, indent=4)


def get_participants(game_id):
    if game_id in data['usergames']:
        user_ids = data['usergames'][game_id]
        participants = []
        for user_id in user_ids:
            try:
                user = bot.get_chat_member(user_id, user_id)
                participants.append(f'{user.user.first_name} (@{user.user.username})')
            except Exception as e:
                print(f"Error getting user info: {e}")
        return '\n'.join(participants)
    return 'Нет участников'


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            chat_id = call.message.chat.id
            user_id = call.from_user.id
            game_id = call.data.split(' ')[1]
            if call.data == f'game {game_id}':
                usergames = data['usergames'].setdefault(game_id, [])
                current_players = len(usergames)
                available_slots = max_players - current_players
                markup = types.InlineKeyboardMarkup(row_width=1)
                if user_id in usergames:
                    item1 = types.InlineKeyboardButton("❌ Отписаться", callback_data=f'leave {game_id}')
                elif available_slots > 0:
                    item1 = types.InlineKeyboardButton(f"✅ Записаться ({available_slots} мест)",
                                                       callback_data=f'join {game_id}')
                else:
                    item1 = types.InlineKeyboardButton(f"❌ Записано максимальное число участников", callback_data='No')
                markup.add(item1)
                bot.send_message(chat_id, "<b>Игра:</b> TTM Board Game"
                                          f"\n<b>Дата:</b> 02.03.2024 19:00"
                                          f"\n<b>Локация:</b> <a href='# location"
                                          f"/'>Кафе Нью Йорк</a>"
                                          f"\n<b>Цена:</b> 1500 руб."
                                          f"\n<b>Свободных мест:</b> {available_slots} из {max_players}"
                                          "\n"
                                          "\n"
                                          "Список участников:\n"
                                          f"{get_participants(game_id)}", parse_mode='html',
                                 reply_markup=markup)
    except Exception as e:
        print(repr(e))

    try:
        if call.message:
            chat_id = call.message.chat.id
            user_id = call.from_user.id

            game_id = call.data.split(' ')[1]

            if call.data.startswith(f'join {game_id}'):
                if game_id in data['usergames']:
                    usergames = data['usergames'][game_id]
                    if user_id not in usergames and len(usergames) < max_players:
                        usergames.append(user_id)
                        bot.send_message(chat_id, f'Вы успешно записаны на игру {game_id}')

                        # Отправка уведомления админу
                        admin_message = (f"Пользователь {call.from_user.first_name} (@{call.from_user.username}) "
                                         f"записался на игру {game_id}")
                        bot.send_message(adminID, admin_message)
                        bot.send_message(adminID1, admin_message)
                        save_data()

            elif call.data.startswith(f'leave {game_id}'):
                if game_id in data['usergames']:
                    usergames = data['usergames'][game_id]
                    if user_id in usergames:
                        usergames.remove(user_id)
                        bot.send_message(chat_id, f'Вы успешно отписались от игры {game_id}')

                        admin_message = (f"Пользователь {call.from_user.first_name} (@{call.from_user.username}) "
                                         f"отписался от игры {game_id}.")
                        bot.send_message(adminID, admin_message)
                        bot.send_message(adminID1, admin_message)
                        save_data()

    except Exception as e:
        print(repr(e))


bot.polling(none_stop=True)
