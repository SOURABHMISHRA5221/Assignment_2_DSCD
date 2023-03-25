import grpc
from concurrent import futures
import time
import registry_pb2_grpc as pb2_grpc
import registry_pb2 as pb2

list_of_servers = []
max_servers = 5
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
        msg = request.message
        print("REQUEST TO ADD SERVER FROM LOCALHOST:"+msg)
        print(msg)
        if ( len(list_of_servers) < max_servers):
            response = "SUCCESS"
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