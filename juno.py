import mimetypes
import re
import os
import jinja2
import handlers

class Juno(object):
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
                'mode':     'dev',
                'scgi_port':    6969,
                'dev_port':     8000,
                '404_template': '404.html',
                '500_template': '500.html',
                'name': 'JunoApp',
                'media_url': '/media/*:file/',
                'media_root': './media/',
                'media_handler': media_serve,
                'template_dir': './templates/',
                }
        if config is not None: self.config.update(config)
        self.config['template_env'] = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.config['template_dir']))
        # set up the media handler    
        self.route(self.config['media_url'], self.config['media_handler'], '*')

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
        return '<Juno: %s>' %self.config['name']

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
        # Transform '/hello/*:name/' forms into '^/hello/(?<name>.*)'
        splat_re = re.compile('^\*?:(?P<var>\w+)$')
        buffer = '^'
        for part in url.split('/'):
            if not part: continue
            match_obj = splat_re.match(part)
            if match_obj is None: buffer += '/' + part
            else: buffer += '/(?P<' + match_obj.group('var') + '>.*)'
        if buffer[-1] != ')': buffer += '/$'        
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
    def __init__(self, request):
        self.headers = request
        if 'DOCUMENT_URI' not in request: request['DOCUMENT_URI'] = '/'
        elif request['DOCUMENT_URI'][-1] != '/': request['DOCUMENT_URI'] += '/'
        self.raw = request
        self.raw['input'] = {}
        self.location = request['DOCUMENT_URI']
        if 'REQUEST_URI' in request:
            self.full_location = request['REQUEST_URI']
        self.parse_query_string('QUERY_STRING')
        self.parse_query_string('POST_DATA')
        if 'POST_DATA' in self.headers:
            del self.headers['POST_DATA']
    
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

def set_config(key, value):
    global _hub
    _hub.config[key] = value

def get_config(key):
    global _hub
    return _hub.config[key] if key in _hub.config else None

class NoViewsAssigned(Exception): pass

def run():
    if _hub: _hub.run()
    else: raise NoViewsAssigned('No urls attached to Juno')

#
#   Functions to add routes based on request methods
#

def route(url=None, method='*'):
    global _hub
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
    global _response
    return _response.append(body)

def header(key, value):
    global _response
    return _response.header(key, value)

#
#   Convenience functions for 404s and redirects
#

def redirect(url):
    global _response
    _response.config['status'] = 302
    _response.config['headers'] = {'Location': url}
    return _response

def notfound(error='Unspecified error', file=None):
    file = file if file else get_config('404_template')
    return template(file).render(error=error)

#
#   Default media serving function
#

def media_serve(web, file):
    file = get_config('media_root') + file
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

def template(path):
    global _hub
    return _hub.config['template_env'].get_template(path)
