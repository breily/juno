
Juno
====

* Juno is a web framework that was designed to make development as fast
  as possible.
* Repository: [http://github.com/breily/juno][repo]
* I have not updated Juno in about 6 years and don't plan to return to it.
  Have fun with it.  It's not a great web framework but there's some
  interesting Python code in it.


Using Juno
----------

To start off:

    from juno import *

    @route('/')
    def index(web):
        return 'Juno says hi'

    run()

Add some url handling:

    @route('/hello/:name/')
    def hello(web, name):
        return 'Hello, %s' %name

Use a template:

    @get('/hi_template/:name/')
    def template_hi(web, name):
        template('hello.html', name=name)

Build a model:

    Person = model('Person', name='string')
    p = Person(name='brian')


Features
--------

* All normal web framework stuff (models, routes, views, templates)
* WSGI compliant, with included development server as well as SCGI/FastCGI servers
* Database access through SQLAlchemy
* Templating included through Jinja2 and Mako, but Juno can use anything.


Install
-------

* You can use easy_install:
    
        easy_install Juno

* Or pull from [Github][repo], and then do:

        $ python setup.py install   # As root
        $ python
        >>> import juno             # Make sure everything worked

* Optional Dependencies: 
    * [SQLAlchemy][sqlalchemy] (for database access)
    * [Jinja2][jinja2]/[Mako][mako] (for templating)
    * [Flup][flup]        (for SCGI/FastCGI only)
    * [Beaker][beaker]      (for sessions)
    * [Werkzeug][werkzeug] (for debugging)


Help / Contribute
-----------------

* See the [doc/][docs] directory for the current documentation.
* More questions? Find bugs? [Check out the new Google group][list].
* Contributions are welcome through Github or by [emailing me a patch][email].


Note
----

* Juno violates some usual principles of good design (don't use global
  variables, don't do things implicitly, etc.) for the sake of fast
  development and less boilerplate code.  You've been warned.


[homepage]:   http://brianreily.com/project/juno
[repo]:       http://github.com/breily/juno/tree/master
[docs]:       http://github.com/breily/juno/tree/master/doc/
[sqlalchemy]: http://www.sqlalchemy.org
[jinja2]:     http://jinja.pocoo.org/2/
[mako]:       http://www.makotemplates.org
[flup]:       http://trac.saddi.org/flup/
[beaker]:     http://wiki.pylonshq.com/display/beaker/Home
[list]:       http://groups.google.com/group/juno-framework
[email]:      mailto:brian@brianreily.com
[wiki]:       http://wiki.github.com/breily/juno/
[q&a]:        http://wiki.github.com/breily/juno/questions-and-answers
[werkzeug]:   http://dev.pocoo.org/projects/werkzeug
