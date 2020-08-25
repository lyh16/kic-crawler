#! /usr/bin/python3

from bitly import shorten_url
import bs4 as b
import collections
import datetime
from dbman import DBMan
import requests as r
import telegram.bot
import time
#from telegram.ext import messagequeue as mq

#변수 등

url_base = 'http://kic.khu.ac.kr'
undergraduate = str(url_base + '/notice/undergraduate/')
jna = str(url_base + '/jobs-activities/')
scholarships = str(url_base + '/notice/scholarships/')
others = str(url_base + '/notice/Others/')

new_pinned = collections.defaultdict(dict)
new_normal = collections.defaultdict(dict)

admins = set(["Admin's Telegram chat_id"])
db = DBMan()
db.setup()

token = 'YOUR TELEGRAM BOT TOKEN'
bot = telegram.Bot(token = token)
#q = mq.MessageQueue()

#함수 및 클래스 정의

def get_pinned(soup):
    '''
    This function fetches the pinned notices in the given webpage.
    '''
    pinned_notices = soup.find_all('tr', {'class':'kboard-list-notice'})
    for notice in pinned_notices:
        for new_icon in notice.find_all('span', {'class':'kboard-default-new-notify'}):
            new_icon.decompose()
        title = notice.find('div', {'class':'kboard-default-cut-strings'}).get_text().strip()
        date = notice.find('td', {'class':'kboard-list-date'}).get_text().strip()
        if ((len(date) == 5) or (len(date) < 5)):
            date = datetime.date.today()
            date = date.strftime("%Y.%m.%d")
        links = notice.find_all('a')
        for a in links:
            if a.has_attr('href'):
                url = a.attrs['href']
                new_pinned[url]['notice_title'] = title
                new_pinned[url]['notice_date'] = date
    return new_pinned

def get_normal(soup):
    '''
    This function fetches the normal notices in the given webpage.
    '''
    normal_notices = soup.find_all('tr', {'class':''})
    for notice in normal_notices:
        for new_icon in notice.find_all('span', {'class':'kboard-default-new-notify'}):
            new_icon.decompose()
        try:
            title = notice.find('div', {'class':'kboard-default-cut-strings'}).get_text().strip()
            date = notice.find('td', {'class':'kboard-list-date'}).get_text().strip()
            if ((len(date) == 5) or (len(date) < 5)):
                date = datetime.date.today()
                date = date.strftime("%Y.%m.%d")
            links = notice.find_all('a')
            for a in links:
                if a.has_attr('href'):
                    url = a.attrs['href']
                    new_normal[url]['notice_title'] = title
                    new_normal[url]['notice_date'] = date
        except:
            pass
    return new_normal

def url_mod(short_link):
    '''
    This function modifies the given short URL to match/become the full URL.
    '''
    full_url = url_base + short_link
    return full_url

def send_notice(channel, text):
    '''
    This function broadcasts the given text to the specified channel via MQBot.
    '''
    #['return' not functioning as expected!!!] return kic_bot.send_message(chat_id = channel, disable_web_page_preview = True, parse_mode = 'HTML', text = text)
    '''
    The below code may be used in place of the above code. But only one may be used at a time.
    The above delegates the message sending function to MQBot.
    The below executes the message sending function directly.
    '''
    return bot.send_message(chat_id = channel, disable_web_page_preview = True, parse_mode = 'HTML', text = text)

def msg_admin(text):
    '''
    This function sends the given text to the hardcoded 'admin(s)'; usually error messages.
    '''
    global admins
    for admin in admins:
        try:
            bot.send_message(chat_id = admin, text = text)
        except:
            pass

class sieve:
    '''
    This class determines whether elements of 'new_data' are new, old, or obsolete compared to 'check_data'.
    '''
    def __init__(self, new_data, check_data):
        self.new_data = new_data
        self.check_data = check_data

    def new(self):
        answer = [x for x in self.new_data if x not in self.check_data]
        return answer

    def old(self):
        answer = [x for x in self.new_data if x in self.check_data]
        return answer

    def obsolete(self):
        answer = [x for x in self.check_data if x not in self.new_data]
        return answer

"""
class MQBot(telegram.bot.Bot):
    '''
    This class is delegated the message sending function.
    Its job is to automatically pace the sending of messages so that the message sending bot does not exceed Telegram's flood control limits.
    '''
    def __init__(self, *args, is_queued_def = True, mqueue = None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        return super(MQBot, self).send_message(*args, **kwargs)

kic_bot = MQBot(token, mqueue = q)
"""

#본 함수

for category in [undergraduate, jna, scholarships, others]:
    if category == undergraduate:
        cat = 'Und'
        channel = '@kic_notices_undergraduate'
    elif category == jna:
        cat = 'JnA'
        channel = '@kic_notices_jna'
    elif category == scholarships:
        cat = 'Sch'
        channel = '@kic_notices_scholarships'
    elif category == others:
        cat = 'Oth'
        channel = '@kic_notices_others'

    response = r.get(category)

    if response.status_code == 200:
        soup = b.BeautifulSoup(response.content, from_encoding = 'utf-8', features = 'html.parser')

        get_pinned(soup)
        check_pinned = db.get_notices(str(cat + '_Pinned'))
        s_p = sieve(new_data = list(new_pinned.keys()), check_data = check_pinned)

        if s_p.new():
            for short_link in s_p.new()[::-1]:
                notice_category = str(cat + '_Pinned')
                notice_date = new_pinned[short_link]['notice_date']
                crawl_dt = datetime.datetime.now()
                title = new_pinned[short_link]['notice_title']

                text_part = notice_date + '\n' + title
                full_url = shorten_url(url_mod(short_link))
                final_notice = '#중요_공지\n' + f'<code>{text_part}</code>' + '\n' + full_url
                msg = send_notice(channel, final_notice)
                msg_id = msg['message_id']
                db.add_notice(notice_category, notice_date, crawl_dt, title, short_link, msg_id)
                time.sleep(2)

        if s_p.obsolete():
            for stuff in s_p.obsolete():
                notice_category = str(cat + '_Pinned')
                message_id = str(db.get_msg_id(notice_category, stuff))
                try:
                    bot.delete_message(chat_id = channel, message_id = message_id)
                except:
                    bot.edit_message_text(text = '#obsolete\n오래된 공지입니다.\n다시 보려면 학과 누리집을 방문해주십시오.' , chat_id = channel, message_id = message_id)
                db.del_notice(notice_category, stuff)

        new_pinned.clear()
        check_pinned.clear()

        get_normal(soup)
        check_normal = db.get_notices(str(cat + '_Normal'))
        s_n = sieve(new_data = list(new_normal.keys()), check_data = check_normal)

        if s_n.new():
            for short_link in s_n.new()[::-1]:
                notice_category = str(cat + '_Normal')
                notice_date = new_normal[short_link]['notice_date']
                crawl_dt = datetime.datetime.now()
                title = new_normal[short_link]['notice_title']

                text_part = notice_date + '\n' + title
                full_url = shorten_url(url_mod(short_link))
                final_notice = f'<code>{text_part}</code>' + '\n' + full_url
                msg = send_notice(channel, final_notice)
                msg_id = msg['message_id']
                db.add_notice(notice_category, notice_date, crawl_dt, title, short_link, msg_id)
                time.sleep(2)

        if s_n.obsolete():
            for stuff in s_n.obsolete():
                notice_category = str(cat + '_Normal')
                message_id = str(db.get_msg_id(notice_category, stuff))
                try:
                    bot.delete_message(chat_id = channel, message_id = message_id)
                except:
                    bot.edit_message_text(text = '#obsolete\n오래된 공지입니다.\n다시 보려면 학과 누리집을 방문해주십시오.' , chat_id = channel, message_id = message_id)
                db.del_notice(notice_category, stuff)

        new_normal.clear()
        check_normal.clear()

    else:
        try:
            response.raise_for_status()
        except r.exceptions.HTTPError as e:
            if response.status_code == 502:
                pass
            else:
                msg_admin(f'CRAWLING FAILED!\n{e}')
            time.sleep(300)
