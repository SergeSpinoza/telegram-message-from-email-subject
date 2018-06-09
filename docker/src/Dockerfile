FROM python:3
MAINTAINER Fedonin Serge <fedonin@gmail.com>

ADD bot-app /opt/bot-app
WORKDIR /opt/bot-app

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./bot.helpdesk.py" ]

