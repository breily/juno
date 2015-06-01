
Juno Requests and Responses
==============================

Request Basics
----------------

Every view in Juno must take a JunoRequest as the first argument.  This
object gives you access to all of the information that the server 
received - headers, GET and POST data, etc.

If 'web' is a JunoRequest object created from an actual request:
            
    web.location        # '/'
    web.full_location   # '/?a=4'
    web.user_agent      # ...user-agent string...
    web.raw             # A dictionary mapping header names to their values
    web.session         # A session object, if 'use_sessions': True
    web['REQUEST_URI']  # The Request can be used like a dictionary, to
                        # retrieve values from the raw dictionary.

Data received from GET/POST requests is stored in web.input().  This
would be query strings (`?a=4&b=5`) and form data.  Currently Juno
does not handle file uploads from forms, but thats at the top of the 
todo list.

To access this data:

    web.input()         # Returns a dictionary of GET/POST data

To access a specific name ('a' in '?a=4'):
    
    web.input('a')      # Gets the value of the GET/POST key 'a'

If multiple values have the same name (i.e. more than one input field
sharing a name), they values are put in a list:
            
    web.input('b')      # => ['1', '2'] for '?b=1&b=2'


To use sessions, be sure to install [Beaker][beaker], and set 'use_sessions'
to True.  Sessions are used like a dictionary:
    
    web.session['foo'] = 'bar'
    web.session.save()  # save() must be called

You then can access 'foo' later on:
    
    web.session['foo']  # => 'bar'


Response Basics
---------------

Juno gives each view a global JunoResponse object when that view is 
called.  You can define your own response object, but is often easier
to use the functions that modify the global object.

A response object is made up of 3 parts:
            
body    &rarr;  Text to send back
status  &rarr;  The HTTP status code
headers &rarr;  Dictionary of HTTP headers

The easiest way to use a response object is through the global
functions, which by default modify a JunoResponse object set to a 
status of 200:

    append(text)       => Add text to the response.  Automatically 
                          updates the Content-Length header.
    header(key, value) => Set a member of the headers dictionary.
    content_type(type) => Specify a Content-Type other than 'text/html'.
    status(code)       => Specify a response code other than 200.

To return a 404 response:
            
    notfound(error, file) => Renders template with a 404 status.
                              error defaults to 'Unspecified error'.
                              file defaults to the value of Juno's
                              '404_template' setting (which you can set
                              when you call init).

To return a 302 (redirect) response:
            
    redirect(url) => Sets the global response to a status of 302 with a 
                             'Location' header set to url.

To return a 500 (server error) response:
            
    servererror(error, file) => Renders the 500_template. error defaults
                                to 'Unspecified error'.

To automatically assign urls, without creating a view to do it:
          
    assign(from, to) => Called from outside of a view, automatically
                        redirects the 'from' url to the 'to' url. 'from'
                        can be a list of urls.

    
Templates
---------

This is probably the most common case of responses, and is covered in
'doc/6-templates.txt'.

    
Static Files
------------

Serving static files with Juno involves 3 configuration options:
            
    'static_url'     => The route that triggers static file serving.  If
                        you change this, you must include a '*:file' 
                        portion (unless you also change the static handler,
                        discussed below).  By default, it is set to
                        '/static/*:file/'.
    'static_root'    => The local directory that Juno looks for static
                        files.  By default, set to './static/'.
    'static_handler' => The view assigned to serve static files.  As noted
                        above, takes a 'file' parameter.  Maps this
                        filename to the 'static_root' directory.

The built in static handler will automatically determine mimetypes for
you, and will return a 404 if the file cannot be found.

[beaker]: http://wiki.pylonshq.com/display/beaker/Home
