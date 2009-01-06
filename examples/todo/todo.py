from juno import *

init({'db_location': 'todo.db'})

Item = model('Item', title='string', desc='string')

@get('/')
def index(web):
    items = find(Item).all()
    return template('index.html', items=items)

@route('/process/')
def process(web):
    title = web.input('title') or ""
    desc = web.input('desc') or ""
    item = Item(title=title, desc=desc).commit()
    redirect('/')

run()
