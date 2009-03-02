import juno

# Initialize Juno here
#  - db_location: urls.db => Create an SQLite database called urls.db
#  - use_debugger: True   => Use the Werkzeug provided debugger
juno.init({'db_location': 'urls.db',
           'use_debugger': True,
          })

# Create a model to store URLs
#  - Juno stores it under the name 'URL'
#  - 'address' and 'tiny' will be VARCHAR fields in your database
URL = juno.model('URL', address='string', tiny='string')

# Set up our first controller
#  - This function will be called when you receive any request for '/'
@juno.route('/')
def index(web):
    # Render our main template
    juno.template('index.html', {'urls': URL.find().all()})

# Set up our preview controller
#  - Displays the actual URL for the 'tiny' version
@juno.get('/p/:tiny/')
def preview_url(web, tiny):
    # Search the database to find the corresponding URL
    url = URL.find().filter(URL.tiny == tiny).one()
    return 'preview: %s' % url.address
 
# Set up our redirecter
#  - We get the short version in our variable 'tiny'
@juno.get('/u/:tiny/')
def get_url(web, tiny):
    url = URL.find().filter(URL.tiny == tiny).one()
    # Redirects the user to the found address
    juno.redirect(url.address)

# Set up a handler to add URLs
@juno.route('/a/')
def add_url_post(web):
    addr = web.input('url')
    if not addr: juno.redirect('/')
    tiny = str(hash(addr))
    url = URL.find().filter(URL.tiny == tiny).first()
    if url is not None:
        return juno.redirect('/p/%s/' % url.address)
    URL(address=addr, tiny=tiny).save()
    juno.redirect('/p/%s/' % tiny)

if __name__ == '__main__': juno.run()
