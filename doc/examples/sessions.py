from juno import *

@get('/foo/')
def foo(web):
    web.session['msg'] = 'hello there'
    web.session.save()
    redirect('/bar/')

@get('/bar/')
def bar(web):
    return web.session['msg']

run()
