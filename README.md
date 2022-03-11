# Local-Mail-To-Request

This repo offers a script to have a local mail server available and post a request for an incoming mail.

## Use-Cases:

IP-Cameras (e.g. Dahua, InStar, ...) often can send mails when an alarm is triggered. They are not able to post an http request.
A Mail can be useful to see it on your smartphone but there is always a lag of time due to a long delivery time. 
Let's assume you want to switch on the light of your smart home based on the cameras alert - far to slow.

With this script, you run a local mail server. The Ip Camera will send a mail immediately (lag of 0.01 s) and you can directly convert it to a html request.

Modify the script as appropriate.

## Installation
Simply run:
> pip install aiosmtpd

## Config of the mail client (e.g. your IP Camera)

I am running the python script on a Raspberry Pi. Simply add the IP address of your Raspberry Pi and the port of the Python script (*here 8025*) to you camera. You can use any dummy mail adresses as it does not matter - the mail stays local in your network.

![image](https://user-images.githubusercontent.com/60820820/157892840-d9d2045c-9fda-4b00-ad12-ed7580f92a9b.png)

## Remarks
My (Dahua) camera didn't properly work with sending mails. Therefore I had to use handle_QUIT. If your's works better, simply use handle_DATA and you will be able to read content of the mail and adapt your processing more detailed.

## Thanks
Thanks to MyDaHua of ipcamtalk for the idea! https://ipcamtalk.com/threads/send-http-request-if-alarm-dahua-ipc-hfw5442e-ze.62080/#post-647785
