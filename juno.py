from scgi_juno import SCGIRequestHandler

import SocketServer

class URLMatchError(Exception): pass

class JunoResponse:
    def __init__(self, body, status, content_type='text/html'):
        self.body = body
        self.status = status
        self.content_type = content_type
        self.content_length = len(body)
    
        self.status_dict = { '200': 'OK' }

    def render(self):
        response = 'HTTP/1.1 %s %s\r\n' %(self.status, self.status_dict[self.status])
        response += 'Content-Type: %s\r\n' %self.content_type
        response += 'Content-Length: %s\r\n' %self.content_length
        response += '\r\n'
        response += '%s' %self.body
        return response

class Juno:
    def __init__(self, urls):
        self.urls = urls

    def run_scgi(self, port=6969):
        SCGIRequestHandler.process = self.process_request
        server = SocketServer.ThreadingTCPServer(('', port), SCGIRequestHandler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.socket.close()
            print 'exiting juno...'
        except:
            print 'error; exiting juno...'
            server.socket.close()

    def process_request(self, request):
        for url in self.urls:
            if url[0] == request['REQUEST_URI']:
                response = url[1](request)
                if type(response) == str:
                    response = JunoResponse(response, '200')
                return response.render()    
        raise URLMatchError()
