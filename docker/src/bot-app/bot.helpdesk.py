import base64, quopri, re
import logging
from imaplib import IMAP4_SSL
from telegram.ext import Updater

### Settings
HOST = "some_server"
PORT = 993
USER = "email_user"
PASSWORD = "password"
bot_token = "telegram_bot_token"
channel_id = "-100xxxxxxxxxxx"
###

# Logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger()

updater = Updater(token=bot_token)
j = updater.job_queue

#Function for convert subject
pat2=re.compile(r'(([^=]*)=\?([^\?]*)\?([BbQq])\?([^\?]*)\?=([^=]*))',re.IGNORECASE)
def decodev2(a):
    data=pat2.findall(a)
    line=[]
    if data:
            for g in data:
                    (raw,extra1,encoding,method,string,extra)=g
                    extra1=extra1.replace('\\r','').replace('\\n','').replace('\\t','').strip()
                    if len(extra1)>0:
                            line.append(extra1)
                    if method.lower()=='q':
                            string=quopri.decodestring(string)
                            string=string.decode().replace("_"," ").strip().encode()
                    if method.lower()=='b':
                            string=base64.b64decode(string)
                    line.append(string.decode(encoding,errors='ignore'))
                    extra=extra.replace('\\r','').replace('\\n','').replace('\\t','').strip()
                    if len(extra)>0:
                            line.append(extra)
            return "".join(line)
    else:
            return a


def callback_messages(bot, job):
    box = IMAP4_SSL(host=HOST, port=PORT)
    box.login(user=USER, password=PASSWORD)
    box.select('INBOX')
    result, ids = box.search(None, 'ALL')
    for id in ids[0].split():
        subject = box.fetch(id,'(BODY.PEEK[HEADER.FIELDS (SUBJECT)])')[1][0][1].strip()
        subject = subject.decode().strip("b'Subject: ")
        subject = decodev2(subject)
        if subject.find("Создано новое задание ID") > -1:
            bot.send_message(chat_id=channel_id, text=subject)
            box.store(id, '+FLAGS', '\\Deleted')  # Delete message
        elif subject.find(" добавлено сообщение") > -1:
            bot.send_message(chat_id=channel_id, text=subject)
            box.store(id, '+FLAGS', '\\Deleted')  # Delete message
        else:
            box.store(id, '+FLAGS', '\\Deleted') # Удаляем сообщение

    box.expunge()
    box.close()
    box.logout()

job_minute = j.run_repeating(callback_messages, interval=30, first=0)
updater.start_polling()

