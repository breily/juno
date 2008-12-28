from juno.juno import Juno
from juno.response import JunoResponse

def index(request):
    body = '''
        <html>
            <head>
                <title>index</title>
            </head>
            <body>
                index
            </body>
        </html>'''
    return JunoResponse(body=body, status='200')

def query(request):
    response = 'Query string: %s' %request.QUERY_STRING
    return response

def form(request):
    body = '''
        <form action='/post_test' name='form_test' method='post'>
            <input type='text' name='word' />
            <input type='text' name='two' />
            <input type='text' name='three' />
            <input type='submit' value='test' />
        </form>'''
    return body

def post_test(request):
    return 'value of "word": %s' %request.post('word')

urls = [
    ['/', index],
    ['/query', query],
    ['/form', form],
    ['/post_test', post_test],
       ]

if __name__ == '__main__':
    Juno(urls).run_scgi()
