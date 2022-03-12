import asyncio
import logging
import requests
import ssl

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import AsyncMessage
from aiosmtpd.smtp import SMTP as Server, syntax
from aiosmtpd.smtp import AuthResult

TOKEN = "abcdefghi"
BASE_URL = "https://192.168.178.86/api/values/"
URL_CAM1 = "url1_cam"
URL_CAM2 = "url2_cam"
IP_CAM1 = '192.168.100.89'
IP_CAM2 = '192.168.100.99'
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
        print("authenticator function called")
        return AuthResult(success=True)

    def factory(self):
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain('cert.pem', 'key.pem')
        return Server(self.handler, tls_context=context, authenticator=self.authenticator_func)


class MyMessageHandler(AsyncMessage):

    async def handle_DATA(self, server, session, envelope):
        print('.....Message from %s' % envelope.mail_from)
        print('.....Message for %s' % envelope.rcpt_tos)
        print('.....Message data:\n')
        for ln in envelope.content.decode('utf8', errors='replace').splitlines():
            print(f'.........> {ln}'.strip())
        print()
        print('.....End of message')

        if session.peer[0] == IP_CAM1:
            url = BASE_URL + URL_CAM1
        elif session.peer[0] == IP_CAM2:
            url = BASE_URL + URL_CAM2

        requests.put(url=url, json={"value": 1}, params={"token": TOKEN}, verify=False)

        return '250 Message accepted for delivery'


async def amain(loop):

    cont = MyController(MyMessageHandler(), hostname='', port=8023)
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
