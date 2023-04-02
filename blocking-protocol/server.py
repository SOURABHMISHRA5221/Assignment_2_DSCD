import grpc
from concurrent import futures
import time
import registry_pb2_grpc as pb2_grpc
import registry_pb2 as pb2
import server_pb2_grpc as spb2_grpc
import server_pb2 as spb2
from datetime import datetime

list_of_replicas = []
primary_server = -1
i_am_primary = True
server_port = 5030
files  = {}
names  = {}
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
            i_am_primary = False
        return result[0]

    def server_write(self,name_,content_,uuid_,port):
        self.host = 'localhost'
        self.server_port = port
        self.channel = grpc.insecure_channel('{}:{}'.format(self.host, self.server_port))
        self.stub = spb2_grpc.ServerStub(self.channel)
        message2 = spb2.Message2(name=name_,content=content_,uuid=uuid_)
        return self.stub.ServerWrite(message2)

    def primary_write(self,name_,content_,uuid_,myPort):
        global primary_server
        self.host = 'localhost'
        self.server_port = primary_server
        self.channel = grpc.insecure_channel('{}:{}'.format(self.host, self.server_port))
        self.stub = spb2_grpc.ServerStub(self.channel)
        message5 = spb2.Message5(name=name_,content=content_,uuid=uuid_,myport=str(myPort))
        return self.stub.PrimaryWrite(message5)





c = PClient(50051)
print(c.register_server(message=str(5030)))



list_of_servers = []
max_servers = 5
primary_server_port = -1
primary_server_client = -1
class ServerService(spb2_grpc.ServerServicer):

    def __init__(self, *args, **kwargs):
        pass

    def RegisterReplicaPrimary(self, request, context):
        message = request.message
        print(message)
        result = {'message': "Done!!!"}
        return spb2.Message(**result)

    def write(self,name,content,uuid):
        global files
        global names
        global list_of_replicas
        if ( uuid not in files):
            if ( name in names):
                #file with name exist
                return "FAIL FE"
            else:
                #new File
                files[uuid][name] = name
                files[uuid][version] = datetime.now()
                f = open(name+'.txt','w')
                f.write(content)
                f.close()
                files[uuid][version] = datetime.now()
                return "SUCCESS"
        else:
            if ( name in names):
                #update File
                f = open(name+'.txt','w')
                f.write(content)
                f.close()
                files[uuid][version] = datetime.now()
                return "SUCCESS"
            else:
                #deleted File
                return "FAIL DF"
        

    def PrimaryWrite(self, request, context):
        global list_of_replicas
        global c
        global primary_server
        name_ = request.name 
        content_ = request.content
        uuid_ = request.uuid 
        myport = int(request.myport)
        mes = self.write(name,content,uuid)
        if (mes == 'SUCCESS'):
            for replica in list_of_replicas:
                if ( replica != myport)
                    c.server_write(name_,content_,uuid_,replica)
            if ( myport != primary_server)
                c.server_write(name_,content_,uuid_,myport)
            result = {'message': mes}
            return spb2.Message(**result)
        elif(mes == "FAIL DF"):
            result = {'message':"File is already deleted" }
            return spb2.Message(**result)
        elif(mes == "FAIL FE"):
            result = {'message':"File with same name exist" }
            return spb2.Message(**result)

    def ServerWrite(self, request, context):
        name_ = request.name 
        content_ = request.content
        uuid_ = request.uuid 
        mes = self.write(name,content,uuid)
        result = {'message': mes}
        return spb2.Message(**result)

    def WriteFile(self, request, context):
        global server_port
        global c
        global i_am_primary
        name_ = request.name 
        content_ = request.content
        uuid_ = request.uuid 
        res = c.primary_write(name_,content_,uuid_,server_port)
        if ( res.message == 'SUCCESS'):
            result = {'status':'SUCCESS','uuid':uuid_,'version':files[uuid_][version]}
            return spb2.Message3(**result)
        else:
            result = {'status':'FAIL','uuid':'NULL','version':'NULL'}
            return spb2.Message3(**result)
    
    def ReadFile(self, request, context):
        uuid_ = request.message
        global files
        if ( uuid_ in files):
            status = "SUCCESS"
            name = files[uuid_][name]
            version = files[uuid_][version]
            f = open(name,'r')
            content = ""
            for line in f:
                content+=line 
            result = {'status':status,'name':name,'content':content,'version':version}
            return spb2.Message4(**result)
        else:
            status = "File Does Not Exist"
            name = 'NULL'
            version = 'NULL'
            content = 'NULL'
            result = {'status':status,'name':name,'content':content,'version':version}
            return spb2.Message4(**result)
    
    def DeleteFile(self, request, context):
        pass

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    spb2_grpc.add_ServerServicer_to_server(ServerService(), server)
    server.add_insecure_port('[::]:5030')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()

