

Juno Tutorial
=============

In this tutorial you'll create a TinyURL type application and learn:
    * How to install Juno
    * How to create and setup a Juno application
    * How to map functions to URLs
    * How to use templates with Juno
    * How to use Juno's model API
    * How to run this as a WSGI application


Installing Juno
---------------

There are two ways to install Juno; the easiest is definitely:
    
    easy_install juno

If you're feeling adventurous, you can pull the latest from Github and use
that:
    
    git pull git://github.com/breily/juno.git
    python setup.py install


Creating a Juno App
-------------------

To make sure Juno is working, we'll create a view that just says
'Hello World'.  Start by creating a file called 'main.py' and importing Juno:
    
    import juno

Next we'll create a function and assign it to an URL (add this to main.py):
    
    @juno.route('/')
    def hello(web):
        return 'Hello, World'

Juno assigns URLs with Python decorators, so in this case any request for '/'
will get sent to our 'hello' function.  juno.route is the most general
decorator, and will route any type of request here.  More specific ones exist -
if you just wanted to send POST requests to this function, you would use
juno.post.

Each of these decorators can take two kinds of argument - either a single string,
as in the above example, or a list of strings:
    
    @juno.route(['/', '/index/'])
    def hello(web):
        return 'Hello, World'

If you use a list of strings, then the function is assigned to each of those URLs.

Next, we'll want to run this so we can see if it works.  At the bottom of main.py,
add:
    
    juno.run()

Now run your script, and go to [http://127.0.0.1:8000](http://127.0.0.1:8000) in
your web browser.


Starting Our TinyURL App
------------------------



URL Handling
------------



Rendering a Template
--------------------



Using GET and POST Data
-----------------------



Using a Database
----------------



Setting Up WSGI
---------------
