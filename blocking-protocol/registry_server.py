import grpc
from concurrent import futures
import time
import registry_pb2_grpc as pb2_grpc
import registry_pb2 as pb2
import server_pb2_grpc as spb2_grpc
import server_pb2 as spb2

class PClient():
    def __init__(self,port):
        self.host = 'localhost'
        self.server_port = port
        self.channel = grpc.insecure_channel('{}:{}'.format(self.host, self.server_port))
        self.stub = spb2_grpc.ServerStub(self.channel)

    def register_replica_primary(self,port):
        message = spb2.Message(message=str(port))
        return self.stub.RegisterReplicaPrimary(message)

list_of_servers = []
max_servers = 5
primary_server_port = -1
primary_server_client = -1
class RegistryService(pb2_grpc.RegistryServicer):

    def __init__(self, *args, **kwargs):
        pass

    def GetServerList(self, request, context):
        message = request.message
        print("SERVER LIST REQUEST FROM "+message)
        global list_of_servers
        response = ""
        for servers in list_of_servers:
            response+=servers+'\n'
        result = {'message': response}
        return pb2.Message(**result)

    def RegisterServer(self, request, context):
        global list_of_servers
        global max_servers
        global primary_server_client
        global primary_server_port
        msg = request.message
        print("REQUEST TO ADD SERVER FROM LOCALHOST:"+msg)
        response = ""
        if ( len(list_of_servers) < max_servers):
            if (primary_server_port == -1):
                primary_server_port = int(msg)
                primary_server_client = PClient(primary_server_port)
                response = "SUCCESS"
            else:
                primary_server_client.register_replica_primary(int(msg))
                response = "SUCCESS "+str(primary_server_port)
            list_of_servers+=["LOCALHOST:"+msg]
        else:
            response = "FAIL"
        result = {'message': response}
        return pb2.Message(**result)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_RegistryServicer_to_server(RegistryService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
