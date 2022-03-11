import asyncio
import logging
import requests

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import AsyncMessage, Debugging

TOKEN = "abcdefghi"
BASE_URL = "https://192.168.178.86/api/values/"
URL_CAM1 = "url1_cam"
URL_CAM2 = "url2_cam"
IP_CAM1 = '192.168.100.89'
IP_CAM2 = '192.168.100.99'

class MyMessageHandler(AsyncMessage):

    async def handle_QUIT(self, server, session, envelope):
        if session.peer[0] == IP_CAM1:
            url = BASE_URL + URL_CAM1
        elif session.peer[0] == IP_CAM2:
            url = BASE_URL + URL_CAM2

        requests.put(url=url, json={"value": 1}, params={"token": TOKEN}, verify=False)

        print("Ready to Quit..")


    # async def handle_DATA(self, server, session, envelope):
    #     # use this if your camera sends the mail right...
 
async def amain(loop):
    cont = Controller(MyMessageHandler(), hostname='', port=8025)
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
