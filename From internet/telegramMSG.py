import requests
import urllib.parse
import json

class BotTelegram:
    
    def __init__(self,token,chatid):
        pass
        self.TOKEN = token
        self.BOTCHATID = chatid
        self.URL = "https://api.telegram.org/bot{}/".format(token)
    

    def send_msg(self,msg):
        safe_string = urllib.parse.quote_plus(msg)
        send_text = self.URL + 'sendMessage?chat_id=' + self.BOTCHATID + '&parse_mode=Markdown&text=' + safe_string
        response = requests.get(send_text)
        return response.json()