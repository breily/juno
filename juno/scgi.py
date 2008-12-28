from request import JunoRequest
import SocketServer

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
        """
        Might not be the best way to parse the SCGI request.  Doesn't use
        the provided length at all, so if for some reason a header starts
        with ',' then it will break (seems unlikely though).
        """
        data_len, data = data.split(':', 1)
        count = 0
        data_list = data.split(chr(0))
        data_dict = { 'len': data_len }
        while data_list[count][0] != ',':
            data_dict[data_list[count]] = data_list[count + 1]
            count += 2
        msg = data_list[count][1:]
        data_dict['POST_DATA'] = msg
        return JunoRequest(data_dict)
    
    def process(self, data): return ''
