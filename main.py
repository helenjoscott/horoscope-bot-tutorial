import os
from datetime import datetime, timedelta

import requests
from telebot import TeleBot

# Create a list of star signs
STAR_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius",
              "Capricorn", "Aquarius", "Pisces"]

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


def get_daily_horoscope(sign: str, day: str) -> dict:
    # Making a change
    """Get daily horoscope for a zodiac sign.
    Keyword arguments:
    sign:str - Zodiac sign
    day:str - Date in format (YYYY-MM-DD) OR TODAY OR TOMORROW OR YESTERDAY
    Return:dict - JSON data
    """
    url = "https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily"
    params = {"sign": sign, "day": day}

    response = requests.get(url, params)

    return response.json()


@bot.message_handler(commands=['horoscope'])
def sign_handler(message):
    user_input = f"What's your zodiac sign?\nChoose one: {STAR_SIGNS}."
    sent_msg = bot.send_message(message.chat.id, user_input, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, day_handler)


def day_handler(message):
    sign = message.text.title()
    if sign in STAR_SIGNS:
        text = "What day do you want to know?\nChoose one: *TODAY*, *TOMORROW*, *YESTERDAY*, or a date in format " \
               "YYYY-MM-DD *up to a year ago*."
        sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
        bot.register_next_step_handler(sent_msg, fetch_horoscope, sign)
    else:
        not_valid = "That was not a valid star sign, try again!"
        bot.send_message(message.chat.id, not_valid)
        sign_handler(message)


def fetch_horoscope(message, sign):
    day = message.text.capitalize()
    # Validate if it's a day or a date
    valid_days = ["Today", "Tomorrow", "Yesterday"]
    if day in valid_days:
        get_horoscope_data(day, message, sign)

    else:
        # Validate that it's a date in the right format
        try:
            date_object = datetime.strptime(day, '%Y-%m-%d')
            # Validate if it's in the prior year
            now = str(datetime.now())
            date_validation(date_object, day, message, now, sign)
        except ValueError:
            invalid_format = "Incorrect data format, should be YYYY-MM-DD"
            bot.send_message(message.chat.id, invalid_format)


def date_validation(date_object, day, message, now, sign):
    if day < now:
        earliest_valid_date = datetime.now() - timedelta(days=365)
        # Validate if the date is in the future
        if date_object >= earliest_valid_date:
            get_horoscope_data(day, message, sign)
        else:
            date_too_old = "The date is too far in the past for my tiny brain, try again"
            bot.send_message(message.chat.id, date_too_old)
    else:
        not_valid = "Date is in the future, try again."
        bot.send_message(message.chat.id, not_valid)


def get_horoscope_data(day, message, sign):
    horoscope = get_daily_horoscope(sign, day)
    data = horoscope["data"]
    horoscope_message = f'*Horoscope details for {sign}, {data["date"]}*: {data["horoscope_data"]}'
    bot.send_message(message.chat.id, "Here's your horoscope!")
    bot.send_message(message.chat.id, horoscope_message, parse_mode="Markdown")


bot.infinity_polling()
