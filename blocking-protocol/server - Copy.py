import grpc
from concurrent import futures
import time
import registry_pb2_grpc as pb2_grpc
import registry_pb2 as pb2
import server_pb2_grpc as spb2_grpc
import server_pb2 as spb2

list_of_replicas = []
primary_server = -1
server_port = 5000
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


c = PClient(50051)
print(c.register_server(message=str(5040)))



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

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    spb2_grpc.add_ServerServicer_to_server(ServerService(), server)
    server.add_insecure_port('[::]:5040')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()

