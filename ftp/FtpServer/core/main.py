import optparse
import socketserver

from core import server
from conf import settings


class ArgvHandler:
    def __init__(self):
        #参数解析
        self.op = optparse.OptionParser()

        #self.op.add_option("-s","--server",dest="server")
        #self.op.add_option("-P","--port",dest="port")
        options,args = self.op.parse_args()
        self.verify_args(options,args)

    #命令分发
    def verify_args(self,options,args):
        cmd = args[0]
        #增加反射，命令分发
        if hasattr(self,cmd):
            func = getattr(self,cmd)
            func()

    def start(self):
        print('the server is working')
        s = socketserver.ThreadingTCPServer((settings.IP,settings.PORT), server.ServerHandler)
        s.serve_forever()

    def help(self):
        pass
