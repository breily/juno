import SocketServer

class Juno:
    def __init__(self, config=None):
        self.urls = []
        self.config = {
                'log':      True,
                'mode':     'scgi',
                'scgi_port': 6969,
                }
        if config is not None:        
            self.config.update(config)

    def run(self):
        if self.config['mode'] == 'scgi':
            SCGIRequestHandler.process = self.process_request
            server = SocketServer.ThreadingTCPServer(
                ('', self.config['scgi_port']), SCGIRequestHandler)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                server.socket.close()
                print '\nexiting juno...'
            except:
                print '\nerror; exiting juno...'
                server.socket.close()
        else:
            print 'error: only scgi is supported now'
            print 'exiting juno...'

    def process_request(self, request):
        if self.config['log']: 
            print request.raw
        for url in self.urls:
            if url.match(request):
                response = url.call()
                if type(response) == str:
                    response = JunoResponse(response, '200')
                return response.render()    
        return JunoResponse('page not found', '404').render()        

    def attach(self, url, func, method):
        if type(url) == str:
            self.urls.append(JunoURL(url, func, method))
        else:
            for u in url:
                self.urls.append(JunoURL(u, func, method))

class JunoURL:
    """Modifiers:
        '*' - Matches previous characted repeated; by itself, matches anything
        '&' - Matches any non-numeric character
        '#' - Matches any numeric character
        ':' - Separator to capture results into names

        Example: '/hello/*:name/' will catch '/hello/brian/', and name = 'brian'
        Example: '/#*/' will match '/1234/', but not '/h123/'
    """    
    modifiers = ['*', '@', '#', ':']
    def __init__(self, url, func, method):
        if url[0] != '/': url = '/' + url
        if url[-1] != '/': url += '/'
        self.url = url
        self.url_parts = url.split('/')
        self.func = func
        self.method = method.upper()
        self.params = []
    
    def match(self, request):
        req_parts = request.DOCUMENT_URI.split('/')
        for a, b in zip(req_parts, self.url_parts):
            # if no modifiers, just check string equality
            if not self.has_modifiers(b): 
                if a == b: continue
                else: return False
            # temporary code to see if it works
            if ':' in b:
                if b.split(':')[0] == '*':
                    self.params.append((b.split(':')[1], a))
                    continue
            # end temporary code
            return False #right?
        if self.method == '*' or self.method == request.REQUEST_METHOD:
            self.request = request
            return True
        return False

    def has_modifiers(self, url):
        """Checks for unescaped modifier characters in url segment."""
        for i in range(len(url)):
            if url[i] not in self.modifiers: continue
            elif i == 0 or b[i - 1] != '\'': return True
        return False
            
    def call(self):
        # this dict() call won't work if some params are named and others aren't
        if self.params:
            return self.func(self.request, **dict(self.params))
        return self.func(self.request)    

    def __repr__(self):
        return '<JunoURL: %s %s - %s()>' %(self.method, self.url, self.func.__name__)

class JunoRequest:
    def __init__(self, request):
        if request['DOCUMENT_URI'][-1] != '/':
            request['DOCUMENT_URI'] += '/'
        self.raw = request
        self.raw['input'] = {}
        self.location = request['DOCUMENT_URI']
        self.full_location = request['REQUEST_URI']
        self.parse_query_string('QUERY_STRING')
        self.parse_query_string('POST_DATA')
    
    def parse_query_string(self, header):
        q = self.raw[header] if header in self.raw else None
        if not q: return
        q = q.split('&')
        for param in q:
            tmp = param.split('=')
            self.raw['input'][tmp[0]] = tmp[1]
        
    def __getattr__(self, attr):
        if attr in self.keys():
            return self.raw[attr]    
        raise NameError()    
        
    def input(self, arg):
        if self.raw['input'].has_key(arg):
            return self.raw['input'][arg]
        return None    

    def __getitem__(self, key): return self.raw[key]
    def __setitem__(self, key, val): self.raw[key] = val
    def keys(self): return self.raw.keys()
    def items(self): return self.raw.items()
    def values(self): return self.raw.values()
    def __len__(self): return len(self.raw)
    def __contains(self, key): return key in self.raw

class JunoResponse:
    status_codes = {'200': 'OK', '302': 'Found', '404': 'Not Found'}
    def __init__(self, body, status='200', content_type='text/html', headers=None):
        self.body = body
        self.status = status
        self.headers = {
            'Content-Length': len(body),
            'Content-Type': content_type,
            }
        headers = headers if headers else {}
        self.headers.update(headers)
    
    def append(self, text):
        self.body += text
        self.headers['Content-Length'] = len(self.body)

    def render(self):
        response = 'HTTP/1.1 %s %s\r\n' %(self.status, self.status_codes[self.status])
        for header, val in self.headers.items():
            response += ': '.join((header, str(val))) + '\r\n'
        response += '\r\n'
        response += '%s' %self.body
        return response

    def header(self, header, value):
        self.headers[header] = value
    
    def __setitem__(self, header, value): self.header(header, value)
    def __getitem__(self, header): return self.headers[header]

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

_hub = None

def init(config=None):
    global _hub
    _hub = _hub if _hub else Juno(config)

def run():
    _hub.run()

def attach(url, method='*'):
    global _hub
    if _hub is None: init()
    def wrap(f):
        _hub.attach(url, f, method)
    return wrap

def post(url):   return attach(url, 'post')
def get(url):    return attach(url, 'get')
def head(url):   return attach(url, 'head')
def put(url):    return attach(url, 'put')
def delete(url): return attach(url, 'attach')
