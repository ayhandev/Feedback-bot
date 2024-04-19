import telebot
from telebot import types
import sqlite3
from datetime import datetime

# Инициализация бота
bot = telebot.TeleBot("your token")  # Замените YOUR_BOT_TOKEN на реальный токен

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    item_add_review = types.KeyboardButton('/add_review')
    item_list_reviews = types.KeyboardButton('/list_reviews')
    markup.row(item_add_review, item_list_reviews)
    bot.send_message(message.chat.id, "Привет! Это бот  Если вы хотите оставить отзыв, нажмите /add_review.", reply_markup=markup)

# Обработчик команды /add_review
@bot.message_handler(commands=['add_review'])
def add_review(message):
    bot.send_message(message.chat.id, "Отправь свой отзыв:")
    bot.register_next_step_handler(message, save_review)


def save_review(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username if message.from_user.username else 'Anonymous'
        review_text = message.text
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect('reviews.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO reviews (user_id, username, review, timestamp) VALUES (?, ?, ?, ?)", (user_id, username, review_text, timestamp))
        conn.commit()
        conn.close()

        bot.send_message(message.chat.id, "Спасибо за отзыв!")
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка: " + str(e))
        print(e)  # Или другой способ логгирования ошибки



# Обработчик команды /list_reviews
@bot.message_handler(commands=['list_reviews'])
def list_reviews(message):
    conn = sqlite3.connect('reviews.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, review, timestamp FROM reviews")
    reviews = cursor.fetchall()
    conn.close()

    if reviews:
        response = "Список отзывов:\n"
        for username, review_text, timestamp in reviews:
            response += f"{username} ({timestamp}): {review_text}\n"
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Список отзывов пуст.")


def init_db():
    conn = sqlite3.connect('reviews.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            user_id INTEGER,
            username TEXT,
            review TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Запуск бота
if __name__ == '__main__':
    init_db() 
    bot.polling(none_stop=True)
