class JunoRequest:
    def __init__(self, request):
        self.data = request
        self.build_query_dict()
        self.build_post_dict()
    
    def build_query_dict(self):
        self.data['query'] = {}
        q = self.data['QUERY_STRING']
        if not q: return
        q = q.split('&')
        for param in q:
            tmp = param.split('=')
            self.data['query'][tmp[0]] = tmp[1]

    def build_post_dict(self):
        self.data['post'] = {}
        q = self.data['POST_DATA']
        if not q: return
        q = q.split('&')
        for param in q:
            tmp = param.split('=')
            self.data['post'][tmp[0]] = tmp[1]

    def keys(self): return self.data.keys()
    def items(self): return self.data.items()
    def values(self): return self.data.values()

    def __getattr__(self, attr):
        if attr == 'query':
            return lambda *arg: self.query(arg)
        if attr == 'post':
            return lambda *arg: self.post(arg)
        if attr in self.keys():
            return self.data[attr]    
        raise NameError()    
        
    def query(self, arg):
        if arg in self.data['query'].keys():
            return self.data['query'][arg]
        raise NameError()

    def post(self, arg):
        if arg in self.data['post'].keys():
            return self.data['post'][arg]
        raise NameError()
