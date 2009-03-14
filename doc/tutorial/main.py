import juno

# Initialize Juno here
#  - db_location: urls.db => Create an SQLite database called urls.db
#  - use_debugger: True   => Use the Werkzeug provided debugger
juno.init({
           'db_location': 'urls.db',
           'use_debugger': True,
          })

# Create a model to store URLs
#  - Juno stores it under the name 'URL'
#  - 'full_address' and 'tiny_address' will be VARCHAR fields in your database
URL = juno.model('URL', full_address='string', tiny_address='string')

# Set up our first controller
#  - This function will be called when you receive any request for '/'
@juno.route('/')
def index(web):
    # Render our main template
    juno.template('index.html')

# Set up our preview controller
#  - Displays the actual URL for the 'tiny' version
@juno.get('/p/:tiny/')
def preview_url(web, tiny):
    # Special command to list all URLs
    # We could put this in a separate view if we wanted
    if tiny == 'all':
        return juno.template('preview.html', {'url_list': URL.find().all()})
    # Search the database to find the corresponding URL
    try:
        url = URL.find().filter(URL.tiny_address == tiny).one()
        juno.template('preview.html', {'url': url})
    # If it's not there, use our 404 page
    except:
        juno.notfound("That preview URL doesn't exist!")

# Set up a handler to add URLs
@juno.route('/a/')
def add_url_post(web):
    # The web.input() function searches both POST data and query strings
    # So we can add using ?url=http://google.com
    # Or have a text input in a form named url
    addr = web.input('url')

    # If we didn't find a url parameter, send us back to home
    if not addr: juno.redirect('/')
    
    # Create a relatively unique tiny representation 
    # http://google.com => 224619259
    tiny = str(abs(hash(addr)))
    
    # Check if this has been created before
    url = URL.find().filter(URL.tiny_address == tiny).first()

    # If it has, send us to the existing preview view
    if url is not None:
        return juno.redirect('/p/%s/' % url.tiny_address)

    # Otherwise add it to the database
    URL(full_address=addr, tiny_address=tiny).save()

    # And show us the preview
    juno.redirect('/p/%s/' % tiny)

# Set up our redirecter
#  - We get the short version in our variable 'tiny'
@juno.get('/:tiny/')
def get_url(web, tiny):
    # Same search that was done in the preview_url() function
    try: 
        url = URL.find().filter(URL.tiny_address == tiny).one()
        # Redirects the user to the found address
        juno.redirect(url.full_address)
    except:
        juno.notfound("That URL doesn't exist")

if __name__ == '__main__': juno.run()
