import os
import poplib
import requests
from configparser import ConfigParser
from email.parser import Parser


def init_config():
    config = ConfigParser()
    config.read(os.path.dirname(os.path.realpath(__file__)) + '/config.ini')
    return config

def get_email_server(config):
    server = poplib.POP3_SSL(config['server'], port=config['port'])
    server.user(config['user'])
    server.pass_(config['password'])
    return server

def get_email(index):
    (resp, lines, octets) = server.retr(index)
    msg_content = b'\r\n'.join(lines).decode('utf-8')
    msg = Parser().parsestr(msg_content)
    return {
        'from': msg.get('From'),
        'subject': msg.get('Subject')
    }

def get_last_email_index():
    with open(os.path.dirname(os.path.realpath(__file__)) + '/email_index', 'r') as file:
        return int(file.read())

def set_last_email_index(index):
    with open(os.path.dirname(os.path.realpath(__file__)) + '/email_index', 'w') as file:
        file.write(str(index))

def telegram_bot_send(config, message):
    url = 'https://api.telegram.org/bot' + config['token'] + '/sendMessage?chat_id=' + config['chat'] + '&parse_mode=Markdown&text=' + message
    response = requests.get(url)
    return response.json()


config = init_config()

server = get_email_server(config['email'])
messages_number = len(server.list()[1])
last_email_index = get_last_email_index()

if (last_email_index < messages_number):
    for index in range(last_email_index, messages_number+1):        
        email = get_email(index)
        telegram_bot_send(config['telegram'], str(index) + "\nFrom: " + email['from'] + "\nSubject: " + email['subject'])
        print('Sent #', index)
    set_last_email_index(messages_number)
    
server.quit()
