import SocketServer
import mimetypes

class Juno:
    def __init__(self, config=None):
        """Takes an optional configuration dictionary. """
        global _hub
        if _hub is not None:
            print 'warning: there is already a Juno object created;'
            print '         you might get some wierd behavior.'
        self.routes = []
        global media_serve
        self.config = {
                'log':      True,
                'mode':     'scgi',
                'scgi_port': 6969,
                '404_template': '',
                '500_template': '',
                'name': 'JunoApp',
                'media_url': '/media/*:file/',
                'media_root': './media/',
                'media_handler': media_serve,
                }
        if config is not None: self.config.update(config)
        self.route(self.config['media_url'], self.config['media_handler'])

    def run(self):
        """Runs the Juno hub, in the set mode (default now is scgi). """
        if self.config['mode'] == 'self':
            print 'Juno would run its own server here...'
        if self.config['mode'] == 'scgi':
            SCGIRequestHandler.process = self.request
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

    def request(self, request):
        """Called when a request is received, routes a url to its request. 
        Returns a string, currently set as a JunoResponse.render()."""
        if self.config['log']: print request.raw
        for route in self.routes:
            if route.match(request):
                response = route.dispatch()
                if response is None:
                    global _response
                    response = _response
                if not isinstance(response, JunoResponse):
                    response = JunoResponse(body=str(response))
                return response.render()    
        return JunoResponse(body='page not found', status=404).render()        

    def route(self, url, func, method='*'):
        """Attaches a view to a url or list of urls, for a given function. """
        if type(url) == str:
            self.routes.append(JunoRoute(url, func, method))
        else:
            for u in url:
                self.routes.append(JunoRoute(u, func, method))

    def __repr__(self):
        return '<Juno: %s>' %self.config['name']

class JunoRoute:
    """Modifiers:
        '*' - Matches previous characted repeated; by itself, matches anything
        ':' - Separator to capture results into names

        Considering: 
            '@' - Matches any non-numeric character
            '#' - Matches any numeric character

        Example: '/hello/*:name/' will catch '/hello/brian/', and name = 'brian'
    """    
    modifiers = ['*', ':']
    def __init__(self, url, func, method):
        if url[0] != '/': url = '/' + url
        if url[-1] != '/': url += '/'
        self.url = url
        self.url_parts = url.split('/')
        self.func = func
        self.method = method.upper()
        self.params = []
    
    def match(self, request):
        """Matches a request uri to this url object. """
        req_parts = request.DOCUMENT_URI.split('/')
        for a, b in zip(req_parts, self.url_parts):
            # if no modifiers, just check string equality
            if not self.has_modifiers(b):
                if a == b: continue
                else: return False
            # just matches '/*:name/' type constructs
            if ':' in b:
                x, y = b.split(':')
                if x in ['*', '']:
                    self.params.append((y, a))
                    continue
            return False
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
            
    def dispatch(self):
        if self.params: return self.func(self.request, **dict(self.params))
        return self.func(self.request)

    def __repr__(self):
        return '<JunoRoute: %s %s - %s()>' %(self.method, self.url, self.func.__name__)

class JunoRequest:
    def __init__(self, request):
        self.headers = request
        del self.headers['POST_DATA']
        if request['DOCUMENT_URI'][-1] != '/':
            request['DOCUMENT_URI'] += '/'
        self.raw = request
        self.raw['input'] = {}
        self.location = request['DOCUMENT_URI']
        self.full_location = request['REQUEST_URI']
        self.parse_query_string('QUERY_STRING')
        self.parse_query_string('POST_DATA')
    
    def parse_query_string(self, header):
        """Adds elements of the query string to ['input'].  If the key
        already appears, make it point to a list of the values. """
        q = self.raw[header] if header in self.raw else None
        if not q: return
        q = q.split('&')
        for param in q:
            k, v = param.split('=', 1)
            if k in self.raw['input'].keys():
                if isinstance(self.raw['input'][k], list):
                    self.raw['input'][k].append(v)
                else: self.raw['input'][k] = [self.raw['input'][k], v]
            else:    
                self.raw['input'][k] = v
        
    def __getattr__(self, attr):
        if attr in self.keys():
            return self.raw[attr]
        raise NameError
        
    def input(self, arg=None):
        if arg is None: return self.raw['input']
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

    def __repr__(self):
        return '<JunoRequest: %s>' %self.location

class JunoResponse:
    status_codes = {200: 'OK', 302: 'Found', 404: 'Not Found'}
    def __init__(self, config=None, **kwargs):
        self.config = {
            'body': '',
            'status': 200,
            'headers': {
                'Content-Type': 'text/html',
            },
        }
        if config is None: config = {}
        self.config.update(config)
        self.config.update(kwargs)
        self.config['headers']['Content-Length'] = len(self.config['body'])
    
    def append(self, text):
        self.config['body'] += text
        self.config['headers']['Content-Length'] = len(self.config['body'])
        return self

    def __iadd__(self, text):
        return self.append(text)

    def render(self):
        response = 'HTTP/1.1 %s %s\r\n' %(self.config['status'],
            self.status_codes[self.config['status']])
        for header, val in self.config['headers'].items():
            response += ': '.join((header, str(val))) + '\r\n'
        response += '\r\n'
        response += '%s' %self.config['body']
        return response

    def header(self, header, value):
        self.config['headers'][header] = value
        return self
    
    def __setitem__(self, header, value): self.header(header, value)
    def __getitem__(self, header): return self.config['headers'][header]

    def __getattr__(self, attr):
        return self.config[attr]

    def __repr__(self):
        return '<JunoResponse: %s %s>' %(self.status, self.status_codes[self.status])

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
        data_dict = {}
        while data_list[count][0] != ',':
            data_dict[data_list[count]] = data_list[count + 1]
            count += 2
        msg = data_list[count][1:]
        data_dict['POST_DATA'] = msg
        return JunoRequest(data_dict)
    
    def process(self, data): return ''

class NoViewsAssigned(Exception): pass

_hub = None

def set_config(config=None):
    global _hub
    _hub = _hub if _hub else Juno(config)

def get_config(key):
    global _hub
    return _hub.config[key] if key in _hub.config else None

def run():
    if _hub: _hub.run()
    else: raise NoViewsAssigned('No urls attached to Juno')

def route(url, method='*'):
    global _hub
    if _hub is None: set_config()
    def wrap(f):
        _hub.route(url, f, method)
    return wrap

def post(url):   return route(url, 'post')
def get(url):    return route(url, 'get')
def head(url):   return route(url, 'head')
def put(url):    return route(url, 'put')
def delete(url): return route(url, 'delete')

_response = None

def redirect(url):
    global _response
    _response = JunoResponse(status=302, body='Location: %s' %url)
    return _response

def respond(**kwargs):
    global _response
    _response = JunoResponse(**kwargs)
    return _response

def notfound(template=None):
    """ Add the 404 template"""
    if template is None: 
        global _hub
        template = _hub.config['404_template'] 
    return JunoResponse(status=404)

def media_serve(web, file):
    global _hub
    file = get_config('media_root') + file
    j = JunoResponse()
    type = mimetypes.guess_type(file)
    if type is not None: j['Content-Type'] = type
    j.append(open(file, 'r').read())
