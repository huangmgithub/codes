### ①-⑤ -->> 链接与验证 ###
### 1-8 -->> 文件上传 ###
### a- -->> 增加进度条 ###
import optparse
import socket
import json
import os
import sys

STATUS_CODE = {
    250:"Invalid cmd format,e.g:{'action':'get','filename':'test.py','size':344}",
    251:"Invalid cmd",
    252:"Invalid auth data",
    253:"Wrong username or password",
    254:"Passed authentication",
    255:"Filename doesn't provided",
    256:"File doesn't exist on server",
    257:"ready to send file",
    258:"md5 verification",

    800:"the file exist,but not enough,is continue?",
    801:"the file exist !",
    802:"ready to receive data",

    900:"md5 validate success"
}

class ClientHandler:
    #①初始化
    def __init__(self):
        #参数解析
        self.op = optparse.OptionParser()

        self.op.add_option("-s","--server",dest="server")
        self.op.add_option("-P", "--port", dest="port")
        self.op.add_option("-u", "--username", dest="username")
        self.op.add_option("-p", "--password", dest="password")

        self.options,self.args = self.op.parse_args()
        #②输入信息验证
        self.verify_args(self.options,self.args)
        #③建立与服务端的链接
        self.make_connection()
        #4.客户端文件路径拼接准备
        self.mainPath = os.path.dirname(os.path.abspath(__file__))
        self.last = 0
    #②输入信息验证
    def verify_args(self,options,args):
        #将输入的信息验证
        server = self.options.server
        port = self.options.port
        #username = options.username
        #password = options.password
        #验证端口是否存在
        if int(port) > 0 and int(port) < 65535:
            return True
        else:
            exit("the port is in 0-65535")
    #③建立与服务端的链接
    def make_connection(self):
        self.sock = socket.socket()
        self.sock.connect((self.options.server,int(self.options.port)))
    #④与服务端进行通信
    def interactive(self):
        #先验证信息是否为空，然后打包发送信息
        if self.authorize():
            #1.客户端信息输入解析
            print("begin to interactive.....")
            cmd_info = input("[%s]" % self.current_dir).strip() ##增加目录选项
            cmd_list = cmd_info.split()
            #2.命令分发
            if hasattr(self,cmd_list[0]):
                func = getattr(self,cmd_list[0])
                func(*cmd_list)
    #3.文件上传功能
    def put(self,*cmd_list):
        #put 12.png images -->> 命令+文件+存放文件夹
        action,local_path,target_path = cmd_list
        #4.文件路径拼接
        local_path = os.path.join(self.mainPath,local_path)
        #5.获得文件名称
        file_name = os.path.basename(local_path)
        #文件大小
        file_size = os.stat(local_path).st_size
        #6.将信息打包
        data = {
            "action":"put",
            "file_name":file_name,
            "file_size":file_size,
            "target_path":target_path
        }
        #7.发送打包后的信息至服务端
        self.sock.send(json.dumps(data).encode('utf-8'))
        ############### 8.文件上传的几种可能情况 ###############
        #8.1收到客户端信息->文件在服务端存在的情况
        is_exist = self.sock.recv(1024).decode('utf-8')
        #已经发送的
        has_sent = 0
        #8.2判断文件是否存在
        if is_exist == "800":
            #8.2.1文件不完整
            #8.2.1用户判断，做出是否继续上传的选择
            choice = input("the file is exist,but not enough,continue?[Y/N]").strip()
            if choice.upper() == "Y":
                #给服务端发送选择信息
                self.sock.sendall("Y".encode('utf-8'))
                #接收服务端发送文件的大小数据
                continue_position = self.sock.recv(1024).decode('utf-8')
                has_sent += int(continue_position) #加上已经存在的内容大小
            else:
                #给服务端发送选择信息
                self.sock.sendall("N".encode('utf-8'))

        elif is_exist == "801":
            #8.2.1文件完整
            print('the file exists')
            return

        #8.3打开文件，读取文件并发送给服务端
        f = open(local_path,'rb')
        f.seek(has_sent) #文件指针指向已经存在的内容的结尾，默认为开始
        while has_sent < file_size:
            data = f.read(1024)
            self.sock.sendall(data)
            has_sent += len(data)
            #a-增加进度条
            self.show_progress(has_sent,file_size)

        f.close()
        print('put success')

    #a-增加进度条
    def show_progress(self,has,total):
        rate = float(has)/float(total)
        rate_num = int(rate*100)
        if self.last != rate_num:
            sys.stdout.write('%s%% %s\r' % (rate_num,'#'*rate_num))
        self.last = rate_num
    #一.ls功能函数
    def ls(self,*cmd_list):
        data = {
            "action":"ls",
        }
        self.sock.sendall(json.dumps(data).encode('utf-8'))
        data = self.sock.recv(1024).decode('utf-8')
        print(data)

    #二.cd功能函数
    def cd(self,*cmd_list):
        #cd images
        data = {
            "action":"cd",
            "dirname":cmd_list[1]
        }
        self.sock.sendall(json.dumps(data).encode('utf-8'))
        data = self.sock.recv(1024).decode('utf-8')
        print(os.path.basename(data))
        self.current_dir = os.path.basename(data)
    #三.mkdir创建文件夹
    def mkdir(self,*cmd_list):
        data = {
            "action":"mkdir",
            "dirname":cmd_list[1]
        }
        self.sock.sendall(json.dumps(data).encode('utf-8'))
        data = self.sock.recv(1024).decode('utf-8')
        print(data)
    #④验证用户名和密码验证是否输入
    def authorize(self):
        #若用户名和密码未输入时，提示重新输入
        if self.options.username is None or self.options.password is None:
            username = input("username:")
            password = input("password:")
            return self.get_auth_result(username,password)
        return self.get_auth_result(self.options.username,self.options.password)

    #④将用户名和密码验证打包发送
    def get_auth_result(self,user,pwd):
        #打包
        data = {
            "action":"auth",
            "username":user,
            "pwd":pwd
        }
        #发送
        self.sock.send(json.dumps(data).encode('utf-8'))
        #⑤接收服务端发送的消息
        response = self.response()
        print("response:",response["status_code"])
        if response["status_code"] == 254:
            #登陆成功后，将user更改为类的属性，可以在其他函数中调用
            self.user = user
            #增加目录选项
            self.current_dir = user
            print(STATUS_CODE[254])
            return True #登陆成功  self.authorize()完成
        else:
            print(STATUS_CODE[response["status_code"]])

    #⑤接收服务端发送的消息
    def response(self):
        data = self.sock.recv(1024).decode('utf-8')
        data = json.loads(data)
        return data

ch = ClientHandler()

ch.interactive()