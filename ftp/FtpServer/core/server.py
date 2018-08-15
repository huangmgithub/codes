### ①-⑤ -->> 链接与验证 ###
### 1-6 -->> 文件上传 ###
################################################
import socketserver
import json
import configparser
from conf import settings
import os

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
    802:"ready to receive datas",

    900:"md5 validate success"
}

class ServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            #①接受客户端发送的消息，1.收到信息并解析
            data = self.request.recv(1024).strip()
            data = json.loads(data.decode('utf-8'))
            #data格式
            '''
            {"action":"auth",
            "username":"yuan",
            "pwd":123
            }
            '''
            #②提取命令  2.提取命令
            if data.get("action"):
                if hasattr(self,data.get("action")):
                    func = getattr(self,data.get("action"))
                    func(**data)#将字典打包
                else:
                    print('cmd cant be found')
            else:
                print("Invalid cmd")
    #③验证功能
    def auth(self,**data):
        username = data["username"]
        password = data["pwd"]
        #④将信息与配置文件进行对比验证
        user = self.authorize(username,password)
        #⑤验证结果发送至客户端
        if user:
            self.send_response(254)
        else:
            self.send_response(253)
    #④将信息与配置文件进行对比验证
    def authorize(self,user,pwd):
        cfg = configparser.ConfigParser()
        cfg.read(settings.ACCOUNT_PATH)

        if user in cfg.sections():
            if cfg[user]["Password"] == pwd:
                #登陆成功后，将user更改为类的属性，可以在其他函数中调用
                self.user = user
                #4.登陆成功后，获得文件存储目录的上级目录，这时的self.user是存在的
                self.mainPath = os.path.join(settings.BASE_DIR,"home",self.user)
                return user
    #⑤验证结果发送至客户端
    def send_response(self,status_code):
        response = {"status_code":status_code}
        self.request.sendall(json.dumps(response).encode('utf-8'))
    #3.文件上传功能
    def put(self,**data):
        print("data",data)
        file_name = data["file_name"]
        file_size = data["file_size"]
        target_path = data["target_path"]
        #5.获得文件存储目录
        abs_path = os.path.join(self.mainPath,target_path,file_name)

        ######## 6.文件上传的几种可能情况 ########
        #已经收到的
        has_received = 0
        #6.0判断文件是否存在
        if os.path.exists(abs_path):
            file_has_size = os.stat(abs_path).st_size
            if file_has_size < file_size:
            ####6.1断点续传，发送信息给客户端
                self.request.sendall("800".encode('utf-8'))
                #6.1.1接受客户端发来的选择信息
                choice = self.request.recv(1024).decode('utf-8')
                if choice == "Y":
                    #发送含部分内容文件的大小
                    self.request.sendall(str(file_has_size).encode('utf-8'))
                    #接着写入模式
                    has_received += file_has_size #加上已经存在的内容大小
                    f = open(abs_path,'ab')
                else:
                    #不续传，直接覆盖掉
                    f = open(abs_path,'wb')

            else:
                #6.2文件完全存在，发送信息给客户端
                self.request.sendall("801".encode('utf-8'))
                return  #终止本循环，开始下一轮循环

        else:
            #6.3文件不存在，发送信息给客户端
            self.request.sendall("802".encode('utf-8'))
            #打开文件，将客户端发来的内容写入文件
            f = open(abs_path,'wb')
        while has_received < file_size:
            #断点续传，若断开客户端服务端会报错，解决办法：增加捕获异常
            try:
                data = self.request.recv(1024)
            except Exception as e:
                break
            f.write(data)
            has_received += len(data)


        f.close()
    #一.ls功能函数
    def ls(self,**data):
        #获得文件列表
        file_list = os.listdir(self.mainPath)
        #变为字符串
        file_str = '\n'.join(file_list)
        #判断是否为空，若为空则必须传一个信息，不然send没有反应
        if not len(file_list):
            file_str = '<empty dir>'
        #发送文件列表到客户端
        self.request.sendall(file_str.encode('utf-8'))
    #二.cd功能函数
    def cd(self,**data):
        dirname = data.get("dirname")
        if dirname == "..":
            self.mainPath = os.path.dirname(self.mainPath)
        else:
            self.mainPath = os.path.join(self.mainPath,dirname)

        self.request.sendall(self.mainPath.encode('utf-8'))
    #三.mkdir创建文件夹
    def mkdir(self,**data):
        dirname = data.get("dirname")
        path = os.path.join(self.mainPath,dirname)
        if not os.path.exists(path):
            if "/" in dirname:
                os.makedirs(path)
            else:
                os.mkdir(path)
            self.request.sendall("create success".encode("utf-8"))
        else:
            self.request.sendall("dirname exist".encode("utf-8"))
