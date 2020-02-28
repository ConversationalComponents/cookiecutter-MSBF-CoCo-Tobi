import httpx


class DirectLineAPI(object):
    """Shared methods for the parsed result objects."""

    def __init__(self, direct_line_secret):
        self._direct_line_secret = direct_line_secret
        self._base_url = 'https://directline.botframework.com/v3/directline'
        self._set_headers()
        self._start_conversation()

    def _set_headers(self):
        headers = {'Content-Type': 'application/json'}
        value = ' '.join(['Bearer', self._direct_line_secret])
        headers.update({'Authorization': value})
        self._headers = headers

    def _start_conversation(self):

        # Start conversation and get us a conversationId to use
        url = '/'.join([self._base_url, 'conversations'])
        botresponse = httpx.post(url, headers=self._headers)

        # Extract the conversationID for sending messages to bot
        jsonresponse = botresponse.json()
        self._conversationid = jsonresponse['conversationId']

    def send_message(self, text):
        """Send raw text to bot framework using directline api"""
        url = '/'.join([self._base_url, 'conversations', self._conversationid, 'activities'])
        jsonpayload = {
            'conversationId': self._conversationid,
            'type': 'message',
            'from': {'id': 'user1'},
            'text': text
        }
        botresponse = httpx.post(url, headers=self._headers, json=jsonpayload)
        if botresponse.status_code == 200:
            return botresponse.json()["id"]
        return "error contacting bot"

    def get_message_response(self, message_id):
        """Get a response message back from the botframework using directline api"""
        url = '/'.join([self._base_url, 'conversations', self._conversationid, 'activities'])
        botresponse = httpx.get(url, headers=self._headers,
                                   ={'conversationId': self._conversationid})
        if botresponse.status_code == 200:
            jsonresponse = botresponse.json()

            responses = [res['text'] for res in jsonresponse['activities']
                         if res.get('replyToId') == message_id]

            if responses:
                return responses[0]
            else:
                return ''

        return "error contacting bot for response"


