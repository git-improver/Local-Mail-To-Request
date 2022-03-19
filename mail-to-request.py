import asyncio
import logging
import requests
import ssl

from config_file import *

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import AsyncMessage
from aiosmtpd.smtp import SMTP as Server, syntax
from aiosmtpd.smtp import AuthResult

from email import message_from_bytes
from email.policy import default


class MyController(Controller):
    @staticmethod
    def authenticator_func(server, session, envelope, mechanism, auth_data):
        # For this simple example, we'll ignore other parameters
        # assert isinstance(auth_data, LoginPassword)
        # username = auth_data.login
        # password = auth_data.password
        # # If we're using a set containing tuples of (username, password),
        # # we can simply use `auth_data in auth_set`.
        # # Or you can get fancy and use a full-fledged database to perform
        # # a query :-)
        # if auth_db.get(username) == password
        return AuthResult(success=True)

    def factory(self):
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain('cert.pem', 'key.pem')
        return Server(self.handler, tls_context=context, authenticator=self.authenticator_func)


class MyMessageHandler(AsyncMessage):

    async def handle_DATA(self, server, session, envelope):
        # Identify Camera that sent the request
        if session.peer[0] == IP_CAMERA_DRIVEWAY:
            url = BASE_URL + URL_DRIVEWAY
        elif session.peer[0] == IP_CAMERA_GARDEN:
            url = BASE_URL + URL_GARDEN

        # Get the message content
        msg = message_from_bytes(envelope.content, policy=default)
        message_content = self.get_message_content(msg).decode()
        # Convert message to list
        message_content_list = []
        for ln in message_content.splitlines():
            print(f'.........> {ln}'.strip())
            message_content_list.append(ln)

        # Extract metadata from message
        alarm_name = None
        for each_line in message_content_list:
            if "Alarm Name: " in each_line:
                alarm_name = each_line.split("Alarm Name: ")[1]

        # Handle based on alarm_name
        normal_alarm_states = ["IVS-TRIPWIRE-GATE",
                               "IVS-TRIPWIRE-MAIN-DOOR",
                               "IVS-TRIPWIRE-SIDE-DRIVEWAY",
                               "IVS-TRIPWIRE-GARDEN",
                               "IVS-INTRUSION-GARDEN"]
        if alarm_name in normal_alarm_states:
            requests.put(url=url, json={"value": 1}, params={"token": TOKEN}, verify=False)
        elif alarm_name == "IVS-MISSING":
            send_pushover_message(title="Missing object in driveway", message=message_content)
        elif alarm_name == "IVS-ABANDONED":
            send_pushover_message(title="Unknown object in driveway", message=message_content)
        else:
            # Send pushover message if alarm name is unknown
            send_pushover_message(title="Unknown camera alarm name", message=message_content)

        return '250 Message accepted for delivery'


    @staticmethod
    def get_message_content(msg):
        """ Get the message content from the mail """
        if msg.is_multipart():
            html = None
            for part in msg.get_payload():
                if part.get_content_charset() is None:
                    # We cannot know the character set, so return decoded "something"
                    text = part.get_payload(decode=True)
                    continue

                charset = part.get_content_charset()

                if part.get_content_type() == 'text/plain':
                    text = str(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')

                if part.get_content_type() == 'text/html':
                    html = str(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')

            if text is not None:
                return text.strip()
            else:
                return html.strip()
        else:
            text = str(msg.get_payload(decode=True), msg.get_content_charset(), 'ignore').encode('utf8', 'replace')
            return text.strip()


def send_pushover_message(title:str = None,
                          message:str = None,
                          attachment:str = None):
    """
    Send a message via pushover to your phone

    """

    data = {
        "token": TOKEN_PUSHOVER,
        "user": USER_KEY_PUSHOVER,
        }
    files = {}
    if title is not None:
        data["title"] = title
    if message is not None:
        data["message"] = message
    if attachment is not None:
        files["attachment"] = ("image.jpg", open(attachment, "rb"), "image/jpeg")

    r = requests.post("https://api.pushover.net/1/messages.json",
                      data=data,
                      files=files)

    return r


async def amain(loop):

    cont = MyController(MyMessageHandler(), hostname='', port=8022)
    cont.start()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.create_task(amain(loop=loop))
    print(".....Starting Job.....")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
