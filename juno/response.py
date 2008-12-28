class JunoResponse:
    def __init__(self, body, status, content_type='text/html', headers=None):
        self.body = body
        self.status = status
        self.content_type = content_type
        self.content_length = len(body)
        self.headers = headers
    
        self.status_dict = { 
            '200': 'OK',
            '302': 'Found',
            '404': 'Not Found',
        }

    def render(self):
        response = 'HTTP/1.1 %s %s\r\n' %(self.status, self.status_dict[self.status])
        response += 'Content-Type: %s\r\n' %self.content_type
        response += 'Content-Length: %s\r\n' %self.content_length
        if self.headers is not None:
            for header in self.headers:
                if header[-2:] != '\r\n': header = header.rstrip() + '\r\n'
                response += header
        response += '\r\n'
        response += '%s' %self.body
        return response
