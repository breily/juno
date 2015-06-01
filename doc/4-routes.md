Juno Routes
===========

Basics
--------

Juno lets you assign functions to a given url by using python decorators:
    
    from juno import *

    @route('/hello/')
    def hello(web): return "Hello there"

The url argument given to the decorator is where this function will be located;
so going to http://127.0.0.1:8000/hello/ will let you see your work.


Multiple URLs for the Same View
---------------------------------

You can replace that one url in the route() function with a list of strings,
like so:
    
    @route(['/', '/index/'])

This lets you send multiple addresses to one view.


Getting the Reqeust Method Involved
-------------------------------------

But what if you want a view to only respond to POST requests? You could do this:
    
    @route('/probably_a_form/', 'post')
    def form_read(web): ...

Since thats pretty verbose, theres a shortcut:
    
    @post('/probably_a_form/')
    ... function ...

There are shortucts for get, post, head, put, and delete.


Handling Wildcard URLs
------------------------

Juno has a very simple URL matching scheme.  Right now there is just one special
character: `*`.  It is used like this:

    @get('/hello/*:person/')
    def hello(web, person): ...

This will match '/hello/brian/' and '/hello/112358/'.  The ':person' part lets us
send the match as a named parameter to your function, which in the preceding 
examples would be 'brian' and '112358'.

Because `*` is the only matching character available now, you don't have to
put it in: `/*:greet/` is the same as '/:greet/'.


Shortcuts
-----------

Juno provides a couple shortcut functions to use with routes.  The first is a 
redirection shortcut.  Instead of writing a function like this:
    
    @route('/')
    def temp(web): redirect('/home/')

The redirect function takes an optional second argument called code, which
defaults to 302:
    
    redirect('/', 303)

You can use the assign function instead:

    assign('/home/', '/')
    assign(['/index/', '/profile/'], '/')

The next allows you to automatically render a template in response to a certain
url:
    
    autotemplate('/about/', 'about.html')

Like assign(), it also accepts a list of urls.

