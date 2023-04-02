import grpc
from concurrent import futures
import time
import registry_pb2_grpc as pb2_grpc
import registry_pb2 as pb2
import server_pb2_grpc as spb2_grpc
import server_pb2 as spb2
import uuid

u_id = str(uuid.uuid1())

files = []
class PClient():
    def __init__(self,port):
        self.host = 'localhost'
        self.server_port = port
        self.channel = grpc.insecure_channel('{}:{}'.format(self.host, self.server_port))
        self.stub = pb2_grpc.RegistryStub(self.channel)

    def register_server(self,message):
        message = pb2.Message(message=message)
        result = self.stub.RegisterServer(message).message.split()
        if (len(result)  != 1):
            primary_server = int(result[1])
        return result[0]

    def get_server_list(self):
        self.host = 'localhost'
        self.server_port = 50051
        self.channel = grpc.insecure_channel('{}:{}'.format(self.host, self.server_port))
        self.stub = pb2_grpc.RegistryStub(self.channel)
        message = pb2.Message(message=u_id)
        return self.stub.GetServerList(message)
    def config(self,port):
        self.host = 'localhost'
        self.server_port = port
        self.channel = grpc.insecure_channel('{}:{}'.format(self.host, self.server_port))
        self.stub = spb2_grpc.ServerStub(self.channel)
    def read(self,file):
        message = spb2.Message(message=u_id)
        return self.stub.ReadFile(message)
    def write(self,uuid_,name_,content_):
        message = spb2.Message2(name =name_,content = content_ ,uuid_ = uuid)
        return self.stub.WriteFile(message)
    def delete(self,file):
        message = spb2.Message(message=file)
        return self.stub.DeleteFile(message)


client = PClient(5100)
print(client.get_server_list().message)

exit_ = False

def displayOptions():
    print("1) Write in file")
    print("2) Read a file")
    print("3) Delete a file")
    print("4) exit")
    return int(input())

while(not exit_):
    v = displayOptions()
    if ( v == 4):
        exit_ = True 
    elif ( v == 1):
        port = int(input("port: "))
        client.config(port)
        res = int(input("Enter 1 to update a new file else 0"))
        file_id = -1
        if ( res == 0):
            for f in range(len(files)):
                print( f,files[f])
            res = int(input("enter file no. "))
            file_id = files[res]
        else:
            new_file = str(uuid.uuid1())
        name    = input("name: ")
        content = input("content: ")
        result = client.write(file_id,name,content)
        print(result.status)
        print(result.uuid)
        print(result.version)
    elif (v == 2):
        port = int(input("port: "))
        client.config(port)
        file_id = '-1'
        for f in range(len(files)):
                print( f,files[f])
        res = int(input("enter file no. "))
        file_id = files[res]
        result  = client.read(file_id)
        print(result.status)
        print(result.name)
        print(result.content)
        print(result.version)
    elif ( v == 3):
        port = int(input("port: "))
        client.config(port)
        file_id = -1
        for f in range(len(files)):
                print( f,files[f])
        res = int(input("enter file no. "))
        file_id = files[res]
        result  = client.delete(file_id)
        print(result.message)

