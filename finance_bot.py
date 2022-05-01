"""Telegram finance bot""" 

# importing all requirements
import requests
from telegram.ext import Filters, MessageHandler, CommandHandler, Updater
from telegram import KeyboardButton, ReplyKeyboardMarkup
from pathlib import Path
import json
from datetime import datetime

# here we are getting out token and creating updater
token = Path.cwd() / 'token.txt'
data = token.open('r')
TOKEN = data.read()
data.close()
updater = Updater(TOKEN)
current_date = str(datetime.now())[:10].split('-')

# buttons for currency
list_of_buttons = [[KeyboardButton('USD')], [KeyboardButton('AUD')], 
                   [KeyboardButton('RUB')], [KeyboardButton('EUR')],
                   [KeyboardButton('RON')], [KeyboardButton('SGD')],
                   [KeyboardButton('NOK')], [KeyboardButton('PLN')],
                   [KeyboardButton('TRY')], [KeyboardButton('XPD')], 
                   [KeyboardButton('LYD')], ]

# all available currency 
values = ('USD', 'AUD', 'RUB', 'EUR', 'RON', 'SGD', 'NOK', 'PLN', 'TRY', 'XPD', 'LYD')


# start command of this bot
def start_bot(update, context):
    chat = update.effective_chat
    user_name = update.message.chat.first_name
    buttons = list_of_buttons
    context.bot.send_message(chat_id=chat.id, text=f'Hi there, {user_name}! I am a finance bot! '
                             'Here you will know all about currency rate! Type /help for more info',
                             reply_markup=ReplyKeyboardMarkup(buttons))


# help command of this bot
def helper(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text="""
1) If you want to know current rate of currency
just click on buttons below 👇
2) If you want to know another rate of currency in
previous years just type something like 2007 or 2018 etc.
                Enjoy 💰""")


def load_file_data(new_data):
    path = Path('data.json')
    data = json.loads(path.read_text(encoding='utf-8'))
    data["info"].append(new_data)
    path.write_text(json.dumps(data, indent=4), encoding='utf-8')


def save_info(user_name, bot_message: list, time, user_message):
    new_data = {'user_name': user_name,
                'user_message': user_message,
                'bot_message': bot_message,
                'time_added': time}
    load_file_data(new_data)


# get current currency rate
def get_currency_rate(currency_code):
    return requests.get(f'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode'
                                    f'={currency_code}&date={current_date[0]}{current_date[1]}{current_date[2]}&json').json()


# get previous currency rate
def get_previous_currency_rate(item, currency_code):
    return requests.get(f'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode={item}&date={currency_code}{current_date[1]}{current_date[2]}&json').json()


# getting and reproducing currency rate from https://bank.gov.ua
def currency_rate(update, context):
    chat = update.effective_chat
    currency_code = update.message.text
    user_name = update.message.chat.first_name
    if currency_code in values:
        current_rate = get_currency_rate(currency_code)
        rate = current_rate[0]['rate']
        message = f"{currency_code} rate: {rate} UAH"
        currency = [message]
        context.bot.send_message(chat_id=chat.id, text=message)
        save_info(user_name, currency, datetime.now().strftime('%A-%d-%B-%Y %H:%M:%S'), currency_code)
    elif currency_code.isdigit():
        currency = []
        for item in values:
            try:
                earlier_rate = get_previous_currency_rate(item, currency_code)
                rate = earlier_rate[0]['rate']
                message = f"{item} rate in {currency_code}: {rate} UAH"
                context.bot.send_message(chat_id=chat.id, text=message)
                currency.append(message)
            except (IndexError, KeyError):
                context.bot.send_message(chat_id=chat.id, text=f'There is no info about {item} 😪')
                continue
        save_info(user_name, currency, datetime.now().strftime('%A-%d-%B-%Y %H:%M:%S'), currency_code)

    else:
        context.bot.send_message(chat_id=chat.id, text='Invalid input!!!')


# creating dispatcher
disp = updater.dispatcher
disp.add_handler(CommandHandler('start', start_bot))
disp.add_handler(CommandHandler('help', helper))
disp.add_handler(MessageHandler(Filters.all, currency_rate))

# starting our bot
updater.start_polling()
updater.idle()
