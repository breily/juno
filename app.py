from juno import *

@get(['/', '/index'])
def index(web):
    body = '''
        <html>
            <head> <title>index</title> </head>
            <body> index </body>
        </html>'''
    return JunoResponse(response_body=body, status=200)

@get('/wildcard/*:name/')
def wildcard(web, name): return str(name)

@get('/x/:a/:b/:c/')
def x(web, a, b, c):
    return str(a) + str(b) + str(c)

@get()
def query(web):
    return 'Query: %s' %web.input()

@route('/form/')
def form_show(web):
    html().title('form test').                                          \
        body().                                                         \
            form(action='/post_test/', name='form_test', method='post').\
                input(type='text', name='one').br().                    \
                input(type='text', name='two').br().                    \
                input(type='text', name='three').br().                  \
                input(type='submit', value='go').                       \
            endform().                                                  \
        endbody().                                                      \
    endhtml()

@post()
def post_test(web): return 'value of "word": %s' %web.post('one')

@get('/json_test/')
def json(web):
    j = JunoResponse()
    j['Content-Type'] = 'application/json'
    return j.append('''{'main': ['a': 5, 'b': 1]}''')

@get('/ua/')
def user_agent(web):
    return 'User Agent: %s' %web.headers['HTTP_USER_AGENT']

@get()
def implicit(web):
    respond(response_body='Hi there')

@get()
def html_chain(web):
    html().                                         \
        head().title('juno html test').endhead().   \
        body().                                     \
            div().text('asdf').enddiv().            \
        endbody().                                  \
    endhtml()

@get('/count/*:times/')
def count(web, times):
    html().head().title('count to %s' %times).endhead().body()
    for i in range(int(times)):
        div(type='counter', id='%s' %i).text("Number: %s" %i).enddiv()
    endbody().endhtml()

if __name__ == '__main__': run()
