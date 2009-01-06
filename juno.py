# Built in library imports
import mimetypes
import re
import os
# Template and DB library imports
import jinja2
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String
from sqlalchemy.orm import sessionmaker, mapper
# Juno library imports
import handlers

class Juno(object):
    def __init__(self, config=None):
        """Takes an optional configuration dictionary. """
        if _hub is not None:
            print 'warning: there is already a Juno object created;'
            print '         you might get some wierd behavior.'
        self.routes = []
        self.config = {
                'log':            True,
                'mode':           'dev',
                'scgi_port':      6969,
                'dev_port':       8000,
                'static_url':     '/static/*:file/',
                'static_root':    './static/',
                'static_handler': static_serve,
                'template_dir':   './templates/',
                '404_template':   '404.html',
                'db_type':        'sqlite',
                'db_location':    '',
                }
        if config is not None: self.config.update(config)
        self.config['template_env'] = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.config['template_dir']))
        # set up the static handler
        self.route(self.config['static_url'], self.config['static_handler'], '*')
        # set up the database (first part ensures correct slash number for sqlite)
        if self.config['db_type'] == 'sqlite':
            if self.config['db_location'] not in ('', ':memory:'):
                self.config['db_location'] = '/' + self.config['db_location']
        eng_name = self.config['db_type'] + '://' + self.config['db_location']
        self.config['db_engine'] = create_engine(eng_name)
        self.config['db_session'] = sessionmaker(bind=self.config['db_engine'])()

    def run(self, mode=None):
        """Runs the Juno hub, in the set mode (default now is scgi). """
        # If a mode is specified, use it. Otherwise use the mode from the config.
        mode = mode if mode else self.config['mode']
        if mode == 'dev':
            handlers.run_dev('', self.config['dev_port'], self.request)
        elif mode == 'scgi':
            handlers.run_scgi('', self.config['scgi_port'], self.request)
        else:
            print 'error: only scgi and the dev server are supported now'
            print 'exiting juno...'

    def request(self, request, method='*', **kwargs):
        """Called when a request is received, routes a url to its request. 
        Returns a string, currently set as a JunoResponse.render()."""
        req_obj = JunoRequest(kwargs)
        if request[-1] != '/': request += '/'
        for route in self.routes:
            if not route.match(request, method): continue
            global _response
            _response = JunoResponse()
            response = route.dispatch(req_obj)
            if response is None: response = _response
            if not isinstance(response, JunoResponse):
                response = JunoResponse(body=str(response))
            return response.render()
        return notfound(error='No matching routes registered')

    def route(self, url, func, method):
        """Attaches a view to a url or list of urls, for a given function. """
        if url is None: url = '/' + func.__name__ + '/'
        if type(url) == str: self.routes.append(JunoRoute(url, func, method))
        else:
            for u in url: self.routes.append(JunoRoute(u, func, method)) 

    def __repr__(self):
        return '<Juno>'

class JunoRoute(object):
    """Uses a simplified regex to grab url parts:
    i.e., '/hello/*:name/' compiles to '^/hello/(?P<name>\w+)/'
    Considering adding '#' to match numbers and '@' to match letters
    i.e. '/id/#:id/' => '^/id/(?P<id>\d+)/'
    and  '/hi/@:name/' => '^/hi/(?P<name>[a-zA-Z])/'
    """
    def __init__(self, url, func, method):
        if url[0] != '/': url = '/' + url
        if url[-1] != '/': url += '/'
        self.old_url = url
        # Transform '/hello/*:name/' forms into '^/hello/(?<name>.*)/'
        splat_re = re.compile('^\*?:(?P<var>\w+)$')
        buffer = '^'
        for part in url.split('/'):
            if not part: continue
            match_obj = splat_re.match(part)
            if match_obj is None: buffer += '/' + part
            else: buffer += '/(?P<' + match_obj.group('var') + '>.*)'
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
        if self.method != '*' and self.method != method: return False
        self.params.update(match_obj.groupdict())
        return True

    def dispatch(self, req):
        return self.func(req, **self.params)

    def __repr__(self):
        return '<JunoRoute: %s %s - %s()>' %(self.method, self.old_url, self.func.__name__)

class JunoRequest(object):
    """Offers following members:
        raw => the header dictionary used to construct the JunoRequest
        location => uri being requested, without query string ('/' from '/?a=6')
        full_location => uri with query string ('/?a=6' from '/?a=6')
        user_agent => the user agent string of requester
    """
    def __init__(self, request):
        # Make sure the request string ends with '/'
        if 'DOCUMENT_URI' not in request: request['DOCUMENT_URI'] = '/'
        elif request['DOCUMENT_URI'][-1] != '/': request['DOCUMENT_URI'] += '/'
        # Set some instance variables
        self.raw = request
        self.raw['input'] = {}
        self.location = request['DOCUMENT_URI']
        if 'REQUEST_URI' in request:
            self.full_location = request['REQUEST_URI']
        # Parse post and get strings    
        self.parse_query_string('QUERY_STRING')
        self.parse_query_string('POST_DATA')
        # Find the right user agent header
        if 'HTTP_USER_AGENT' in request: self.user_agent = request['HTTP_USER_AGENT']
        elif 'User-Agent' in request: self.user_agent = request['User-Agent']
        else: self.user_agent = '?'
    
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
        return None

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

class JunoResponse(object):
    status_codes = {200: 'OK', 302: 'Found', 404: 'Not Found'}
    def __init__(self, config=None, **kwargs):
        self.config = {
            'body': '',
            'status': 200,
            'headers': { 'Content-Type': 'text/html', },
        }
        if config is None: config = {}
        self.config.update(config)
        self.config.update(kwargs)
        self.config['headers']['Content-Length'] = len(self.config['body'])
    
    def append(self, text):
        self.config['body'] += str(text)
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

#
#   Functions to deal with the global Juno object (_hub)
#

_hub = None

def init(config=None):
    global _hub
    _hub = _hub if _hub else Juno(config)
    return _hub

def config(key, value=None):
    if value is None:
        if type(key) == dict: _hub.config.update(key)
        else: return _hub.config[key] if key in _hub.config else None
    else: _hub.config[key] = value    

def run(mode=None):
    if _hub is None: init()
    _hub.run(mode)

#
#   Functions to add routes based on request methods
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
    file = file if file else get_config('404_template')
    return append(template(file).render(error=error))

#
#   Default static file serving function
#

def static_serve(web, file):
    file = get_config('static_root') + file
    if not os.access(file, os.F_OK):
        return notfound(error='media file could not be located')
    if os.path.isdir(file):
        return notfound(error='that location is a directory')
    type = mimetypes.guess_type(file)[0]
    if type is not None: header('Content-Type', type)
    else: header('Content-Type', 'text/plain')
    return append(open(file, 'r').read())

#
#   Templating
#

def template(template_path, template_dict=None, **kwargs):
    t = _hub.config['template_env'].get_template(template_path)
    if not kwargs and not template_dict: return t
    if template_dict: return append(t.render(template_dict))
    return append(t.render(kwargs))

#
#   Functions to make tests easier
#

def test_request(path): return _hub.request(path)

#
#   Data modeling functions
#

class JunoClassConstructor(type):
    def __new__(cls, name, bases, dct):
        return type.__new__(cls, name, bases, dct)
    def __init__(cls, name, bases, dct):
        super(JunoClassConstructor, cls).__init__(name, bases, dct)

# Map the class name to the class
models = {}
# Map SQLAlchemy's types to string versions of them for convenience
column_mapping = {'string': String, 'str': String,
                  'integer': Integer, 'int': Integer, }

def model(model_name, **kwargs):
    if not _hub: init()
    # Parse kwargs to get column definitions
    cols = [ Column('id', Integer, primary_key=True), ]
    for k, v in kwargs.items():
        if type(v) == str:
            v = v.lower()
            if v in column_mapping: v = column_mapping[v]
            else: raise NameError("'%s' is not an allowed database column" %v)
        cols.append(Column(k, v))
    # Functions for the class
    def __init__(self, **kwargs):
        for k, v in kwargs.items(): self.__dict__[k] = v
    def add(self): session().add(self)
    def commit(self):
        session().add(self)
        session().commit()
    def __repr__(self): return '<%s: id = %s>' %(self.__name__, self.id)
    # Create the class    
    tmp = JunoClassConstructor(model_name, (object,), {'__name__': model_name, 
        '__init__': __init__, 'add': add, 'commit': commit, '__repr__': __repr__})
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

session = lambda: config('db_session')

