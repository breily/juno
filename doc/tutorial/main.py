import juno
import httplib, urlparse # For checking URL validity

# Initialize Juno here
#  - db_location: urls.db => Create an SQLite database called urls.db
#  - use_debugger: True   => Use the Werkzeug provided debugger
juno.init({
    'db_location': 'urls.db',
    'use_debugger': True,
    })

# Create a model to store URLs
#  - Juno stores it under the name 'URL'
#  - address and tiny will be VARCHAR fields in your database
URL = juno.model('URL', address='string', tiny='string')

# Set up our first controller
#  - This function will be called when you receive any request for '/'
@juno.route('/')
def index(web):
    juno.template('index.html', {'urls': URL.find().all()})

@juno.get('/p/:tiny/')
def preview_url(web, tiny):
    url = URL.find().filter(URL.tiny == tiny).all()
    print url
    if len(url) == 0:
        return error('no such url')
    if len(url) == 1:
        return 'preview: %s' % str(url[0].address)
    return error('somehow multiple (%s) urls with same id' % len(url))
    

@juno.get('/u/:tiny/')
def get_url(web, tiny):
    url = URL.find().filter(URL.tiny == tiny).all()
    if len(url) == 0:
        return error('no such url')
    if len(url) == 1:
        return juno.redirect(url[0].address)
    return error('somehow multiple urls with same id')

@juno.get('/a/:addr/')
def add_url(web, addr):
    # Doesn't pull in parts of url after #
    tiny = str(hash(addr))
    url = URL.find().filter(URL.tiny == tiny).all()
    if len(url) != 0:
        return juno.redirect('/p/%s/' % url[0].address)
    if url_valid(addr): 
        URL(address=addr, tiny=tiny).save()
        return juno.redirect('/p/%s/' % tiny)
    if url_valid('http://%s' % addr): 
        URL(address='http://%s'% addr, tiny=tiny).save()
        return juno.redirect('/p/%s/' % tiny)
    return error('that url is not valid')


@juno.post('/a/')
def add_url_post(web):
    addr = web.input('address')
    if not addr: juno.redirect('/')
    tiny = str(hash(addr))
    url = URL.find().filter(URL.tiny == tiny).all()
    if len(url) != 0:
        return juno.redirect('/p/%s/' % url[0].address)
    if url_valid(addr): 
        URL(address=addr, tiny=tiny).save()
        return juno.redirect('/p/%s/' % tiny)
    if url_valid('http://%s' % addr): 
        URL(address='http://%s'% addr, tiny=tiny).save()
        return juno.redirect('/p/%s/' % tiny)
    return error('that url is not valid')

def error(msg):
    print 'Error: %s' % msg
    return 'Error: %s' % msg

def url_valid(address):
    host, path = urlparse.urlsplit(address)[1:3]
    try:
        conn = httplib.HTTPConnection(host)
        conn.request("HEAD", path)
        response = conn.getresponse()
        if response.status in [404,]: return False
    except:
        return False
    return True

if __name__ == '__main__': juno.run()
