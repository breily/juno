import sys
import platform

class Client(object):
    def __init__(self, application, **kwargs):
        """
        Creates a client to send requests to a WSGI application.
        Parameters:
            - application: A WSGI application callable
            - **kwargs: Any changes/additions to the environ dictionary
        """
        self.application = application
        self.environ = {
            # CGI Variables
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'QUERY_STRING': '',
            'CONTENT_TYPE': '',
            'CONTENT_LENGTH': '',
            'SERVER_PORT': '8000',
            'SERVER_NAME': platform.uname()[1],
            'SERVER_PROTOCOL': 'HTTP/1.1',
            # WSGI Variables
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': None,
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
        }
        self.environ.update(kwargs)

    def request(self, PATH_INFO='/', **kwargs):
        """
        Requests PATH_INFO from the client's application.
        Parameters:
            - PATH_INFO: Requested path, defaults to '/'
            - **kwargs: Any request specific changes/additions to environ
        """
        self.environ['PATH_INFO'] = PATH_INFO
        # Add in custom headers
        self.environ.update(kwargs)
        def start_response(status, headers):
            self.status = status
            self.headers = headers
        self.body = self.application(self.environ, start_response)
        return (self.status, self.headers, self.body)

    def get_header(self, query):
        """
        Retrieve a header's tuple from the response based on name.
        """
        query = query.lower()
        for k, v in self.headers:
            if k.lower() == query: return (k, v)
        raise Exception
