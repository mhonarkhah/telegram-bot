import json
import requests
import time
import urllib
import datetime

from dbhelper import DBHelper

db = DBHelper()

TOKEN = "380854366:AAHyf2AtGbclMcuhk-JrG2XNPjy35IiTijI"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def get_output_summary_string(summary_result, numdays=1):
    output_string = ''
    year, month, day = db.get_date_tuple(numdays)
    if numdays == 1:
        output_string += '*voice stats for today*\n'
    else:
        output_string += '*voice stats since  {}/{}/{}*\n'.format(month, day, year)
    if len(summary_result) > 0:
        count_length = max([len(str(person[1])) for person in summary_result])
    else:
        count_length = 1
    summary_result_srted = sorted(summary_result, key=lambda x: x[2], reverse=True)
    for i, person in enumerate(summary_result_srted):
        first_name = person[0]
        count      = person[1]
        duration   = str(datetime.timedelta(seconds=person[2]))
        output_string += '`{:8}` *{{* num:`{:<{}}`, time: `{}` *}}*\n'.format(first_name, count, count_length, duration)
    if output_string == '':
        output_string = 'The database is empty now'
    return output_string
    
    
def handle_updates(updates):
    for update in updates["result"]:
        #print(update)
        text = 'ok'
        if 'message' in update:
            if 'text' in update['message']:
                text = update["message"]["text"]
    
            chat = update["message"]["chat"]["id"]
            if text == "/summary":
                summary_result = db.get_summaries()
                output_string = get_output_summary_string(summary_result)
                send_message(output_string, chat)
            elif text.startswith('/summary'):
                numdays = text[8:]
                try:
                    numdays = int(numdays)
                    if numdays <=0:
                        send_message("Number of days has to be positive >1.", chat)
                    else:
                        summary_result = db.get_summaries(numdays)
                        output_string = get_output_summary_string(summary_result, numdays)
                        send_message(output_string, chat)
                except ValueError:
                    send_message("the day number is incorrect format, please provide a positive integer for how many days in the past you are looking for.", chat)
            elif text == "/start":
                send_message("Welcome to your personal voice message total duration database storage and calculator. Type /summary to get the stats for the day.", chat)
            elif text == "/reset":
                db.delete_old_messages()
            elif text == "/resetall":
                db.delete_all()
            elif text.startswith("/total since "):
                hour = text[13:]
                try:
                    hour = int(hour)
                    if hour < 0 or hour > 23:
                        send_message("Wrong message, hour has to be between 0 and 23", chat)
                    else:
                        first_name = update['message']['from']['first_name']
                        seconds = db.get_total(hour)
                        if seconds is None:
                            seconds = 0
                        total = str(datetime.timedelta(seconds=seconds))
                        output_string = '`Thank you `{}` for the inquiry.`\n'.format(first_name)
                        output_string += '`Total voices since {}:00:00 for you is: `{}'.format(hour,total)
                        send_message(output_string, chat)
                except ValueError:
                    send_message("The hour is not provided correctly. It has to be between 0 and 23. For example: `/total since 13`", chat)
            elif text == "/help":
                output_string  = '*List of commands: *\n'
                output_string += '`{:15}`: summary for today\n'.format('/summary')
                output_string += '`{:15}`: summary for last _n_ days\n'.format('/summary n')
                output_string += '`{:15}`: total voices today since hour _h_\n'.format('/total since h')
                send_message(output_string, chat)
            elif text.startswith("/"):
                continue
            elif 'voice' in update['message']:
                db.add_voice(update['message'])
            else:
                continue



def build_keyboard(items):
    keyboard = [[user] for user in db.get_user_list]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


def main():
    db.setup()
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(1.0)


if __name__ == '__main__':
    main()