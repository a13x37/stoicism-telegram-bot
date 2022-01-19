import requests


class BotHandler():

    def __init__(self, token):
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def send_message(
            self,
            chat_id,
            text,
            parse_mode=None,
            disable_web_page_preview=None,
            reply_markup=None):
        params = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': disable_web_page_preview,
            'reply_markup': reply_markup
            }
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def remove_webhook(self, drop_updates: bool = None):
        method = 'deleteWebhook'
        params = {'drop_pending_updates': drop_updates}
        resp = requests.post(self.api_url + method, params)
        return resp

    def set_webhook(self, url: str):
        method = 'setWebhook'
        params = {'url': url}
        resp = requests.post(self.api_url + method, params)
        return resp

    def getWebhookInfo(self):
        method = 'getWebhookInfo'
        resp = requests.get(self.api_url + method)
        webhookinfo = resp.json()
        return webhookinfo
