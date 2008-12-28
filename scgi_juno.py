import sys
import SocketServer

SCGI_PORT = 6969

class SCGILengthError(Exception): pass

class SCGIRequestHandler(SocketServer.BaseRequestHandler):
    def finish(self):
        self.request.close()
        print self.client_address, 'disconnected'

    def handle(self):
        data = self.request.recv(1024)
        if data: 
            request_dict = self.build_scgi_dict(data)
            self.request.send(self.process(request_dict))
        self.request.close()

    def build_scgi_dict(self, data):
        data_len, data = data.split(':', 1)
        if len(data) != int(data_len) + 1:
            raise SCGILengthError()
        count = 0
        data_list = data.split(chr(0))
        data_dict = { 'len': data_len }
        while data_list[count] != ',':
            data_dict[data_list[count]] = data_list[count + 1]
            count += 2
        return data_dict    
    
    def process(self, data): return ''

def custom_process(self, data):
    response_body = '''
        <html>
            <head>
                <title>%s</title>
            </head>
            <body>
                you used %s to request %s
            </body>
        </html>''' %(data['REQUEST_URI'], data['REQUEST_METHOD'], 
            data['REQUEST_URI'])
    response = ['HTTP/1.1 200 OK', 
                'Content-Type: text/html', 
                'Content-Length: %s' %len(response_body),
                '', 
                response_body]
    return '\r\n'.join(response)

if __name__ == '__main__':
    SCGIRequestHandler.process = custom_process
    server = SocketServer.ThreadingTCPServer(('', SCGI_PORT), SCGIRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print 'exiting...'
        sys.exit(0)
