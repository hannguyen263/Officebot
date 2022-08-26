import re
import json
import time
import logging
import traceback

# noinspection PyPackageRequirements
import telebot
# noinspection PyPackageRequirements
from telebot import types

from code import Code
from office_user import OfficeUser


file = open("config.json", encoding="utf8")
config = json.load(file)

bot = telebot.TeleBot(
    token=config['bot']['token'],
    parse_mode='HTML'
)

user_dict = {
    # 'user_id': {
    #     'selected_sub': {},
    #     'selected_domain': '',
    #     'username': '',
    #     'code': ''
    # }
}

OU = OfficeUser(
    client_id=config['aad']['clientId'],
    tenant_id=config['aad']['tenantId'],
    client_secret=config['aad']['clientSecret']
)
C = Code()

#logging.basicConfig(level=logging.DEBUG)
def start(m):
  # logging.debug(m)
    if m.from_user.id == config['bot']['admin']:
        bot.send_message(
            text='Welcome to use <b>Office User Bot</b>\n\n'
                 'The available commands are：\n'
                 '/create Create Office account\n'
                 '/gen 10 generates ten activation codes\n'
                 '/about About Bot',
            chat_id=m.from_user.id
        )

    else:
        bot.send_message(
            text='Welcome to <b>Office User Bot</b>\n\n'
                 'The available commands are:\n'
                 '/create Create Office account\n'
                 '/about About Bot',
            chat_id=m.from_user.id
        )


def gen(m):
    #print("TELE RECEIVED")
    #print(m.from_user.id)
    #print(type(m.from_user.id))
    #print("CONFIG ADMIN")
    #print(config['bot']['admin'])
    #print(type(config['bot']['admin']))
    if m.from_user.id == int(config['bot']['admin']):
        #print("inside ")
        amount = int(str(m.text).strip().split('/gen')[1].strip())
        codes = C.gen(amount)
        bot.send_message(
            text='\n'.join(codes),
            chat_id=m.from_user.id
        )

def about(m):
    bot.send_message(
        text='<a href="https://t.me/hannguyen12">Contact admin</a>',
        chat_id=m.from_user.id
    )


def create(m):
    buttons = [types.KeyboardButton(
        text=sub['name']
    ) for sub in config['office']['subscriptions']]

    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(*buttons)
    msg = bot.send_message(
        text='Welcome to create an Office account\n\nPlease choose a subscription:',
        chat_id=m.from_user.id,
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, select_subscription)


def select_subscription(m):
    selected_sub = next(
        (sub for sub in config['office']['subscriptions'] if sub['name'] == m.text),
        None
    )
    if selected_sub is None:
        msg = bot.send_message(
            text='The subscription does not exist, please reply again:',
            chat_id=m.from_user.id,
        )
        bot.register_next_step_handler(msg, select_subscription)
        return
    user_dict[m.from_user.id] = {}
    user_dict[m.from_user.id]['selected_sub'] = selected_sub

    markup = types.ReplyKeyboardRemove(selective=False)
    msg = bot.send_message(
        text='Please reply with the desired username:',
        chat_id=m.from_user.id,
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, input_username)


def input_username(m):
    username = str(m.text).strip()
    if username in config['banned']['officeUsername'] or \
            not re.match(r'^[a-zA-Z0-9\-]+$', username):
        msg = bot.send_message(
            text='The username contains special characters or is in the blacklist, please reply again: ',
            chat_id=m.from_user.id,
        )
        bot.register_next_step_handler(msg, input_username)
        return
    user_dict[m.from_user.id]['username'] = username

    buttons = [types.KeyboardButton(
        text=d['display']
    ) for d in config['office']['domains']]
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(*buttons)
    msg = bot.send_message(
        text='Please select account suffix: ',
        chat_id=m.from_user.id,
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, select_domain)


def select_domain(m):
    selected_domain = next(
        (d for d in config['office']['domains'] if d['display'] == m.text),
        None
    )
    if selected_domain is None:
        msg = bot.send_message(
            text='The suffix does not exist, please reply again: ',
            chat_id=m.from_user.id,
        )
        bot.register_next_step_handler(msg, select_domain)
        return
    user_dict[m.from_user.id]['selected_domain'] = selected_domain

    markup = types.ReplyKeyboardRemove(selective=False)
    msg = bot.send_message(
        text='Please reply with the activation code: ',
        chat_id=m.from_user.id,
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, input_code)


def input_code(m):
    code = str(m.text).strip()
    if not C.check(code):
        bot.send_message(
            text='Invalid activation code!',
            chat_id=m.from_user.id,
        )
        return
    # todo: lock code
    user_dict[m.from_user.id]['code'] = code

    selected_sub_name = user_dict[m.from_user.id]['selected_sub']['name']
    selected_domain_display = user_dict[m.from_user.id]['selected_domain']['display']
    username = user_dict[m.from_user.id]['username']

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='Cancel', callback_data='cancel'),
        types.InlineKeyboardButton(text='Create', callback_data='create'),
    )
    bot.send_message(
        text=f'{selected_sub_name}\n'
             f'{username}@{selected_domain_display}\n\n'
             'The activation code is valid, are you sure to create an account? ',
        chat_id=m.from_user.id,
        reply_markup=markup
    )


def notify_admin(call):
    if config['bot']['notify']:
        user_id = call.from_user.id

        selected_sub_name = user_dict[user_id]['selected_sub']['name']
        selected_domain_value = user_dict[user_id]['selected_domain']['value']
        username = user_dict[user_id]['username']
        code = user_dict[user_id]['code']
        tg_name = f'{call.from_user.first_name or ""} {call.from_user.last_name or ""}'.strip()

        bot.send_message(
            text=f'<a href="tg://user?id={user_id}">{tg_name}</a> Just used the activation code {code} created '
                 f'{username}{selected_domain_value} ({selected_sub_name})',
            chat_id=config['bot']['admin']
        )


def create_account(call):
    user_id = call.from_user.id
    msg_id = call.message.message_id
    chat_id = call.from_user.id

    if user_dict.get(user_id) is None:
        return

    bot.edit_message_text(
        chat_id=chat_id,
        text='Please wait while creating an account...',
        message_id=msg_id
    )
   # logging.basicConfig(level=logging.DEBUG)
    try:
        account = OU.create_account(
            username=user_dict[user_id]['username'],
            domain=user_dict[user_id]['selected_domain']['value'],
            sku_id=user_dict[user_id]['selected_sub']['sku'],
            display_name=f'{call.from_user.first_name or ""} {call.from_user.last_name or ""}'.strip(),
        )
      #  logging.debug(account)
        C.del_code(user_dict[user_id]['code'])

        selected_sub_name = user_dict[user_id]['selected_sub']['name']
      #  logging.debug(selected_sub_name)
        bot.send_message(
            text='Account created successfully\n'
                 '===========\n\n'
                 f'Subscription: {selected_sub_name}\n'
                 f'Mail: <b>{account["email"]}</b>\n'
                 f'Initial password: <b>{account["password"]}</b>\n\n'
                 f'Login address: https://office.com',
            chat_id=chat_id
        )

        notify_admin(call)
        del user_dict[user_id]

    except Exception as e:
        error = json.loads(str(e))
        if 'userPrincipalName already exists' in error['error']['message']:
            text = 'The user name already exists, please change the user name to re-create the account '

        else:
            text = 'Oops something went wrong'

        bot.send_message(
            text=text,
            chat_id=chat_id
        )


@bot.message_handler(content_types=['text'])
def handle_text(m):
    # noinspection PyBroadException
    try:
        if m.from_user.id in config['banned']['tgId']:
            return

        text = str(m.text).strip()

        bot.send_chat_action(
            chat_id=m.from_user.id,
            action='typing'
        )
        if text == '/create':
            create(m)

        elif text == '/about':
            about(m)

        elif text.startswith('/gen'):
            gen(m)

        else:
            start(m)

    except Exception:
        traceback.print_exc()


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == 'create':
        create_account(call)

    elif call.data == 'cancel':
        bot.edit_message_text(
            chat_id=call.from_user.id,
            text='Cancelled',
            message_id=call.message.message_id
        )


def main():

    logger = telebot.logger
    telebot.logger.setLevel(logging.DEBUG)

    bot.polling(none_stop=True)


if __name__=="__main__":
    while True:
        try:
            main()
        except:
            time.sleep(10)
