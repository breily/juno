from scgi import SCGIRequestHandler
from response import JunoResponse

from SocketServer import ThreadingTCPServer

class Juno:
    def __init__(self, urls, log=True):
        self.urls = urls
        self.log = True

    def run_scgi(self, port=6969):
        SCGIRequestHandler.process = self.process_request
        server = ThreadingTCPServer(('', port), SCGIRequestHandler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.socket.close()
            print '\nexiting juno...'
        except:
            print '\nerror; exiting juno...'
            server.socket.close()

    def process_request(self, request):
        if self.log:
            print request.data
        for url in self.urls:
            if url[0] == request.DOCUMENT_URI:
                response = url[1](request)
                if type(response) == str:
                    response = JunoResponse(response, '200')
                return response.render()    
        return JunoResponse('page not found', '404').render()        
