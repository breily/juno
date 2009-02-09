# Built in library imports
import mimetypes
import re
import os
import sys
# Template and DB library imports
import jinja2
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String
from sqlalchemy import Unicode, Text, UnicodeText, Date, Numeric, Time, Float
from sqlalchemy import DateTime, Interval, Binary, Boolean, PickleType
from sqlalchemy.orm import sessionmaker, mapper
# Server imports
import SocketServer
import BaseHTTPServer
import urlparse
import cgi
from wsgiref.simple_server import make_server


class Juno(object):
    def __init__(self, config=None):
        """Takes an optional configuration dictionary. """
        if _hub is not None:
            print 'warning: there is already a Juno object created;'
            print '         you might get some weird behavior.'
        self.routes = []
        # Set options and merge in user-set options
        self.config = {
                'log':            True,
                'mode':           'dev',
                'scgi_port':      8000,
                'dev_port':       8000,
                'wsgi_port':      8000,
                'static_url':     '/static/*:file/',
                'static_root':    './static/',
                'static_handler': static_serve,
                'template_root':  './templates/',
                '404_template':   '404.html',
                'db_type':        'sqlite',
                'db_location':    ':memory:',
                }
        if config is not None: self.config.update(config)
        # Set up Jinja2
        self.config['template_env'] = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.config['template_root']))
        # set up the static file handler
        self.route(self.config['static_url'], self.config['static_handler'], '*')
        # set up the database (first part ensures correct slash number for sqlite)
        if self.config['db_type'] == 'sqlite':
            self.config['db_location'] = '/' + self.config['db_location']
        eng_name = self.config['db_type'] + '://' + self.config['db_location']
        self.config['db_engine'] = create_engine(eng_name)
        self.config['db_session'] = sessionmaker(bind=self.config['db_engine'])()

    def run(self, mode=None):
        """Runs the Juno hub, in the set mode (default now is scgi). """
        # If a mode is specified, use it. Otherwise use the mode from the config.
        mode = mode if mode else self.config['mode']
        if mode == 'dev':
            run_dev('', self.config['dev_port'], self.request)
        elif mode == 'scgi':
            run_scgi('', self.config['scgi_port'], self.request)
        elif mode == 'wsgi':
            run_wsgi('', self.config['wsgi_port'], self.request)
        else:
            print 'error: only scgi, wsgi and the dev server are supported now'
            print 'exiting juno...'

    def request(self, request, method='*', **kwargs):
        """Called when a request is received, routes a url to its request. 
        Returns a string, currently set as a JunoResponse.render()."""
        if self.log: print '%s request for %s...' %(method, request)
        req_obj = JunoRequest(kwargs)
        # Set the global response object in case the view wants to use it
        global _response
        _response = JunoResponse()
        # Add a slash if there isn't one - avoids frustrating matching bugs
        if request[-1] != '/': request += '/'
        for route in self.routes:
            if not route.match(request, method): continue
            if self.log: print '%s matches, calling %s()...\n' %(
                route.old_url, route.func.__name__)
            # Get the return from the view    
            response = route.dispatch(req_obj)
            # If nothing returned, use the global object
            if response is None: response = _response
            # If we don't have a string, render the Response to one
            if isinstance(response, JunoResponse):
                return response
            return JunoResponse(body=response)
        # No matches - 404
        if self.log: print 'No match, returning 404...\n'
        return notfound(error='No matching routes registered')

    def route(self, url, func, method):
        """Attaches a view to a url or list of urls, for a given function. """
        # An implicit route - the url is just the function name
        if url is None: url = '/' + func.__name__ + '/'
        # If we just have one url, add it
        if type(url) == str: self.routes.append(JunoRoute(url, func, method))
        # Otherwise add each url in the list
        else:
            for u in url: self.routes.append(JunoRoute(u, func, method)) 

    def __getattr__(self, attr): 
        return self.config[attr] if attr in self.config else None

    def __repr__(self): return '<Juno>'

class JunoRoute(object):
    """Uses a simplified regex to grab url parts:
    i.e., '/hello/*:name/' compiles to '^/hello/(?P<name>\w+)/'
    Considering adding '#' to match only numbers and '@' to match only letters
    i.e. '/id/#:id/' => '^/id/(?P<id>\d+)/'
    and  '/hi/@:name/' => '^/hi/(?P<name>[a-zA-Z])/'
    """
    def __init__(self, url, func, method):
        # Make sure the url begins and ends in a '/'
        if url[0] != '/': url = '/' + url
        if url[-1] != '/': url += '/'
        # Store the old one before we modify it (we use it for __repr__)
        self.old_url = url
        # RE to match the splat format
        splat_re = re.compile('^\*?:(?P<var>\w+)$')
        # Start building our modified url
        buffer = '^'
        for part in url.split('/'):
            # Beginning and end portions are empty
            if not part: continue
            match_obj = splat_re.match(part)
            # If it doesn't match, just add it without modification
            if match_obj is None: buffer += '/' + part
            # Otherwise replace it with python's regex format
            else: buffer += '/(?P<' + match_obj.group('var') + '>.*)'
        # If we don't end with a wildcard, add a end of line modifier    
        if buffer[-1] != ')': buffer += '/$'
        else: buffer += '/'
        self.url = re.compile(buffer)
        self.func = func
        self.method = method.upper()
        self.params = {}

    def match(self, request, method):
        """Matches a request uri to this url object. """
        match_obj = self.url.match(request)
        if match_obj is None: return False
        # Make sure the request method matches
        if self.method != '*' and self.method != method: return False
        # Store the parts that matched
        self.params.update(match_obj.groupdict())
        return True

    def dispatch(self, req):
        """Calls the route's view with any named parameters."""
        return self.func(req, **self.params)

    def __repr__(self):
        return '<JunoRoute: %s %s - %s()>' %(self.method, self.old_url, 
                                             self.func.__name__)

class JunoRequest(object):
    """Offers following members:
        raw => the header dictionary used to construct the JunoRequest
        location => uri being requested, without query string ('/' from '/?a=6')
        full_location => uri with query string ('/?a=6' from '/?a=6')
        user_agent => the user agent string of requester
    """
    def __init__(self, request):
        # Make sure we have a request uri, and it ends in '/'
        if 'DOCUMENT_URI' not in request: request['DOCUMENT_URI'] = '/'
        elif request['DOCUMENT_URI'][-1] != '/': request['DOCUMENT_URI'] += '/'
        # Set some instance variables
        self.raw = request
        self.raw['input'] = {}
        self.location = request['DOCUMENT_URI']
        # If we get a REQUEST_URI, store it.  Otherwise copy DOCUMENT_URI.
        if 'REQUEST_URI' in request:
            self.full_location = request['REQUEST_URI']
        else: self.full_location = self.location
        # Build the input dict
        self.combine_request_dicts()
        # Find the right user agent header
        if 'HTTP_USER_AGENT' in request: self.user_agent = request['HTTP_USER_AGENT']
        elif 'User-Agent' in request: self.user_agent = request['User-Agent']
        else: self.user_agent = '?'
    
    def combine_request_dicts(self):
        input_dict = self.raw['GET_DICT'].copy()
        for k, v in self.raw['POST_DICT'].items():
            # Combine repeated keys
            if k in input_dict.keys(): input_dict[k].extend(v)
            # Otherwise just add this key
            else: input_dict[k] = v
        # Escape each item in the input dict
        for k, v in input_dict.items():
            input_dict[k] = [cgi.escape(i) for i in v]
        # Reduce the dict - change one item lists ([a] to a)
        for k, v in input_dict.items():
            if len(v) == 1: input_dict[k] = v[0]
        self.raw['input'] = input_dict

    def __getattr__(self, attr):
        # Try returning values from self.raw
        if attr in self.keys():
            return self.raw[attr]
        return None

    def input(self, arg=None):
        # No args: return the whole dictionary
        if arg is None: return self.raw['input']
        # Otherwise try to return the value for that key
        if self.raw['input'].has_key(arg):
            return self.raw['input'][arg]
        return None

    # Make JunoRequest as a dictionary for self.raw
    def __getitem__(self, key): return self.raw[key]
    def __setitem__(self, key, val): self.raw[key] = val
    def keys(self): return self.raw.keys()
    def items(self): return self.raw.items()
    def values(self): return self.raw.values()
    def __len__(self): return len(self.raw)
    def __contains(self, key): return key in self.raw

    def __repr__(self):
        return '<JunoRequest: %s>' %self.location

class JunoResponse(object):
    status_codes = {200: 'OK', 302: 'Found', 404: 'Not Found'}
    def __init__(self, config=None, **kwargs):
        # Set options and merge in user-set options
        self.config = {
            'body': '',
            'status': 200,
            'headers': { 'Content-Type': 'text/html', },
        }
        if config is None: config = {}
        self.config.update(config)
        self.config.update(kwargs)
        self.config['headers']['Content-Length'] = len(self.config['body'])
    
    # Add text and adjust content-length
    def append(self, text):
        self.config['body'] += str(text)
        self.config['headers']['Content-Length'] = len(self.config['body'])
        return self
 
    # Implement +=
    def __iadd__(self, text):
        return self.append(text)

    # Write to a string
    def render(self):
        response = 'HTTP/1.1 %s %s\r\n' %(self.config['status'],
            self.status_codes[self.config['status']])
        for header, val in self.config['headers'].items():
            response += ': '.join((header, str(val))) + '\r\n'
        response += '\r\n'
        response += '%s' %self.config['body']
        return response

    # Set a header value
    def header(self, header, value):
        self.config['headers'][header] = value
        return self
 
    # Modify the headers dictionary when the response is treated like a dict
    def __setitem__(self, header, value): self.header(header, value)
    def __getitem__(self, header): return self.config['headers'][header]

    def __getattr__(self, attr):
        return self.config[attr]

    def __repr__(self):
        return '<JunoResponse: %s %s>' %(self.status, self.status_codes[self.status])

#
#   Functions to deal with the global Juno object (_hub)
#

_hub = None

def init(config=None):
    """Set up Juno with an optional configuration."""
    global _hub
    _hub = _hub if _hub else Juno(config)
    return _hub

def config(key, value=None):
    """Get or set configuration options."""
    if value is None:
        if type(key) == dict: _hub.config.update(key)
        else: return _hub.config[key] if key in _hub.config else None
    else: _hub.config[key] = value    

def run(mode=None):
    """Start Juno, with an optional mode argument."""
    if _hub is None: init()
    if len(sys.argv) > 1:
        if '-mode=' in sys.argv[1]: mode = sys.argv[1].split('=')[1]
        elif '-mode' == sys.argv[1]: mode = sys.argv[2]
    _hub.run(mode)

#
#   Decorators to add routes based on request methods
#

def route(url=None, method='*'):
    if _hub is None: init()
    def wrap(f): _hub.route(url, f, method)
    return wrap

def post(url=None):   return route(url, 'post')
def get(url=None):    return route(url, 'get')
def head(url=None):   return route(url, 'head')
def put(url=None):    return route(url, 'put')
def delete(url=None): return route(url, 'delete')

#
#   Functions to deal with the global response object (_response)
#

_response = None

def append(body):
    """Add text to response body. """
    global _response
    return _response.append(body)

def header(key, value):
    """Set a response header. """
    global _response
    return _response.header(key, value)

def content_type(type):
    """Set the content type header. """
    header('Content-Type', type)

#
#   Convenience functions for 404s and redirects
#

def redirect(url):
    global _response
    _response.config['status'] = 302
    # clear the response headers and add the location header
    _response.config['headers'] = { 'Location': url }
    return _response

def assign(from_, to):
    if type(from_) not in (list, tuple): from_ = [from_]
    for url in from_:
        @route(url)
        def temp(web): redirect(to)

def notfound(error='Unspecified error', file=None):
    """Appends the rendered 404 template to response body. """
    file = file if file else config('404_template')
    return append(template(file).render(error=error))

#
#   Serve static files.
#

def static_serve(web, file):
    """The default static file serve function. Maps arguments to dir structure."""
    file = config('static_root') + file
    if not yield_file(file): notfound("that file could not be found/served")

def yield_file(filename, type=None):
    """Append the content of a file to the response. Guesses file type if not
    included.  Returns 1 if requested file can' be accessed (often means doesn't 
    exist).  Returns 2 if requested file is a directory.  Returns 7 on success. """
    if not os.access(filename, os.F_OK): return 1
    if os.path.isdir(filename): return 2
    if type is None:
        guess = mimetypes.guess_type(filename)[0]
        if guess is None: content_type('text/plain')
        else: content_type(guess)
    else: content_type(type)
    append(open(filename, 'r').read())
    return 7

#
#   Templating
#

def template(template_path, template_dict=None, **kwargs):
    """Append a rendered template to response.  If template_dict is provided,
    it is passed to the render function.  If not, kwargs is."""
    t = get_template(template_path)
    if not kwargs and not template_dict: return append(t.render())
    if template_dict: return append(t.render(template_dict))
    return append(t.render(kwargs))

def get_template(template_path):
    """Returns a Jinja2 template object."""
    return _hub.config['template_env'].get_template(template_path)

def autotemplate(urls, template_path):
    """Automatically renders a template for a given path.  Currently can't
    use any arguments in the url."""
    if type(urls) not in (list, tuple): urls = urls[urls]
    for url in urls:
        @route(url)
        def temp(web): template(template_path)

####
#   Data modeling functions
####

class JunoClassConstructor(type):
    def __new__(cls, name, bases, dct):
        return type.__new__(cls, name, bases, dct)
    def __init__(cls, name, bases, dct):
        super(JunoClassConstructor, cls).__init__(name, bases, dct)

# Map the class name to the class
models = {}
# Map SQLAlchemy's types to string versions of them for convenience
column_mapping = {     'string': String,       'str': String,
                      'integer': Integer,      'int': Integer, 
                      'unicode': Unicode,     'text': Text,
                  'unicodetext': UnicodeText, 'date': Date,
                      'numeric': Numeric,     'time': Time,
                        'float': Float,   'datetime': DateTime,
                     'interval': Interval,  'binary': Binary,
                      'boolean': Boolean,     'bool': Boolean,
                   'pickletype': PickleType,
                 }

session = lambda: config('db_session')

def model(model_name, **kwargs):
    if not _hub: init()
    # Functions for the class
    def __init__(self, **kwargs):
        for k, v in kwargs.items(): self.__dict__[k] = v
    def add(self): session().add(self)
    def commit(self):
        session().add(self)
        session().commit()
    def __repr__(self): return '<%s: id = %s>' %(self.__name__, self.id)
    cls_dict = {'__init__': __init__, 'add': add, 'commit': commit,
                '__name__': model_name, '__repr__': __repr__ }
    # Parse kwargs to get column definitions
    cols = [ Column('id', Integer, primary_key=True), ]
    for k, v in kwargs.items():
        if callable(v):
            cls_dict[k] = v
            continue
        if type(v) == str:
            v = v.lower()
            if v in column_mapping: v = column_mapping[v]
            else: raise NameError("'%s' is not an allowed database column" %v)
        cols.append(Column(k, v))
    # Create the class    
    tmp = JunoClassConstructor(model_name, (object,), cls_dict)
    # Create the table
    metadata = MetaData()
    tmp_table = Table(model_name + 's', metadata, *cols)
    metadata.create_all(config('db_engine'))
    # Map the table to the created class
    mapper(tmp, tmp_table)
    # Add class and functions to global namespace
    global models
    models[model_name] = tmp
    globals()['find_' + model_name.lower()] = lambda: find(tmp)
    globals()[model_name] = tmp
    return tmp

def find(model_cls):
    if type(model_cls) == str:
        try: model_cls = models[model_cls]
        except: raise NameError("No such model exists ('%s')" %model_cls)
    return session().query(model_cls)

####
#   Juno's Servers - Development and SCGI
####

def serve(server):
    try:
        server.serve_forever()
    except:
        print 'interrupted; exiting juno...'
        server.socket.close()

class HTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self): self.do_request()
    def do_POST(self): self.do_request()
    def do_PUT(Self): self.do_request()
    def do_HEAD(self): self.do_request()
    def do_DELETE(self): self.do_request()
    
    def do_request(self):
        parsed = urlparse.urlparse(self.path)
        data_dict = {
             'REQUEST_URI': self.path, 
             'REQUEST_METHOD': self.command,
             'QUERY_STRING': parsed.query, 
             'DOCUMENT_URI': parsed.path if parsed.path[-1] == '/' else parsed.path + '/',
             'GET_DICT': cgi.parse_qs(parsed.query, keep_blank_values=1),
        }
        # TODO: Fix this, see TODO file      
        # perhaps: self.headers.getheader('content-type')
        data = str(self.headers).split('\r\n')
        for line in data:
            if not line: continue
            (x, y) = [a.strip() for a in line.split(':', 1)]
            data_dict[x] = y
        # find POST data
        if self.command == 'POST':
            data_dict['POST_DATA'] = self.rfile.read(int(data_dict['Content-Length']))
        else: data_dict['POST_DATA'] = ''
        # Build POST dictionary
        data_dict['POST_DICT'] = cgi.parse_qs(data_dict['POST_DATA'],
                                    keep_blank_values=1)
        self.wfile.write(self.process(parsed.path, self.command, **data_dict))

    def process(self, uri, method='*', **kwargs): return ''

def run_dev(addr, port, process_func):
    # All the dev server does is take the JunoResponse and render it
    def http_handler(self, uri, method='*', **kwargs):
        juno_response = process_func(uri, method, **kwargs)
        return juno_response.render()
    HTTPRequestHandler.process = http_handler
    server = BaseHTTPServer.HTTPServer((addr, port), HTTPRequestHandler)
    if addr == '': addr = '127.0.0.1'
    print ''
    print 'running Juno development server, <C-c> to exit...'
    print 'connect to %s:%s to use your app...' %(addr, port)
    print ''
    serve(server)

class SCGIRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        if data:
            request_dict = self.build_scgi_dict(data)
            uri = request_dict['DOCUMENT_URI']
            method = request_dict['REQUEST_METHOD']
            self.request.send(self.process(uri, method, **request_dict))
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
        # Build POST and GET dictionaries
        data_dict['POST_DICT'] = cgi.parse_qs(data_dict['POST_DATA'],
                                    keep_blank_values=1)
        data_dict['GET_DICT'] = cgi.parse_qs(data_dict['QUERY_STRING'],
                                    keep_blank_values=1)
        return data_dict
    
    def process(self, uri, method='*', **kwargs): return ''

def run_scgi(addr, port, process_func):
    # All SCGI does is take the JunoResponse and render it
    def scgi_handler(self, uri, method='*', **kwargs):
        juno_response = process_func(uri, method, **kwargs)
        return juno_response.render()
    SCGIRequestHandler.process = scgi_handler
    server = SocketServer.TCPServer((addr, port), SCGIRequestHandler)
    if addr == '': addr = '127.0.0.1'
    print ''
    print 'running Juno SCGI server, <C-c> to exit...'
    print 'connect to %s:80 to use your app...' %addr
    print ''
    serve(server)

# Sets up and runs a test WSGI server.  Doesn't talk to a real server yet.
def run_wsgi(addr, port, process_func):
    def wsgi_handler(environ, start_response):
        # Ensure some environ variables exist (WSGI doesn't guarantee these)
        if not environ['PATH_INFO']: environ['PATH_INFO'] = '/'
        if not environ['QUERY_STRING']: environ['QUERY_STRING'] = ''
        if not environ['CONTENT_LENGTH']: environ['CONTENT_LENGTH'] = '0'
        # Standardize some header names
        environ['DOCUMENT_URI'] = environ['PATH_INFO']
        if environ['QUERY_STRING']:
            environ['REQUEST_URI'] = environ['PATH_INFO']+'?'+environ['QUERY_STRING']
        else:
            environ['REQUEST_URI'] = environ['DOCUMENT_URI']
        # Parse query string arguments
        if environ['REQUEST_METHOD'] == 'GET':
            environ['GET_DICT'] = cgi.parse_qs(environ['QUERY_STRING'], 
                                               keep_blank_values=1)
        else: environ['GET_DICT'] = {}
        if environ['REQUEST_METHOD'] == 'POST':
            # Read from the POST file, skipping read errors or errors formatting
            # the Content-Length header
            try:
                post_data = environ['wsgi.input'].read(int(environ['CONTENT_LENGTH']))
            except:
                post_data = ''
            environ['POST_DICT'] = cgi.parse_qs(post_data,
                                                keep_blank_values=1)
        else: environ['POST_DICT'] = {}
        # WSGI request is now ready to pass to Juno
        juno_response = process_func(environ['DOCUMENT_URI'],
                                     environ['REQUEST_METHOD'],
                                     **environ)
        # Make a status string of '%(status code) %(status string)'
        status = juno_response.config['status']
        status = '%s %s' %(status, juno_response.status_codes[status])
        # Make sure every header is a string
        headers = [(str(k), str(v)) for k, v in 
                   juno_response.config['headers'].items()]
        # WSGI uses start_response to return status and headers
        start_response(status, headers)
        # Then return the body
        return [juno_response.config['body']]
    httpd = make_server(addr, port, wsgi_handler)
    if addr == '': addr = '127.0.0.1'
    print ''
    print 'running Juno WSGI server, <C-c> to exit...'
    print 'connect to %s:%s to use your app...' %(addr, port)
    print ''
    httpd.serve_forever()

