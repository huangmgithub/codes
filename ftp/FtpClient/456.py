from socket import *
import sys

ip_port = ('169.254.53.3',8050)
buffer_size = 1024

ftp_client = socket(AF_INET,SOCK_STREAM)
ftp_client.connect(ip_port)

while True:
    msg = input('->:').strip()
    if not msg:continue
    if msg == 'quit':break
    #发送消息
    ftp_client.send(msg.encode('utf-8'))
    #接收消息
    data = ftp_client.recv(buffer_size)
    print('收到来自服务端的消息',data.decode('utf-8'))

ftp_client.close()