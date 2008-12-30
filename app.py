from juno import *

@get(['/', '/index'])
def index(request):
    body = '''
        <html>
            <head> <title>index</title> </head>
            <body> index </body>
        </html>'''
    return JunoResponse(body=body, status='200')

@get('/wildcard/*:name/')
def hmmm(request, name):
    return str(name)

@get('/query/')
def query(request):
    response = 'Query string: %s' %request.QUERY_STRING
    return response

@attach('/form/')
def form(request):
    body = '''
        <form action='/post_test' name='form_test' method='post'>
            <input type='text' name='word' />   <br />
            <input type='text' name='two' />    <br />
            <input type='text' name='three' />  <br />
            <input type='submit' value='test' />
        </form>'''
    return body

@post('/post_test/')
def post_test(request):
    return 'value of "word": %s' %request.post('word')

@get('/json_test/')
def json(request):
    j = JunoResponse('', '200')
    j['Content-Type'] = 'text/json'
    j.append('''{'main': ['a': 5, 'b': 1]}''')
    return j

if __name__ == '__main__': run()
