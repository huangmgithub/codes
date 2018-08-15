import socketserver
import subprocess
import struct

class Myserver(socketserver.BaseRequestHandler):
    def handle(self):
        print('conn is',self.request)
        print('addr is',self.client_address)

        while True:  #通信循环
            try:
                cmd = self.request.recv(buffer_size)
                if not cmd:break
                print('客户端发送来的命令是:',cmd.decode('utf-8'))
                res = subprocess.Popen(cmd.decode('utf-8'),shell=True,
                                       stderr=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stdin=subprocess.PIPE)
                err = res.stderr.read()
                if err:
                    cmd_res = err
                else:
                    cmd_res = res.stdout.read()
                if not cmd_res:
                    cmd_res = '执行成功'.encode('gbk')
                #先发数据长度，避免粘包
                length = len(cmd_res)
                data_length = struct.pack('i',length)
                self.request.send(data_length)
                self.request.send(cmd_res)
            except Exception as e:
                print(e)
                break

if __name__ == '__main__':
    ip_port = ('169.254.53.3', 8050)
    buffer_size = 1024
    s = socketserver.ThreadingTCPServer(ip_port,Myserver)
    print(s.server_address)
    print(s.RequestHandlerClass)
    s.serve_forever()


