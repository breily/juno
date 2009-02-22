
Setup
=====

Installation
------------

Juno consists of just one Python module, and is installed with the usual
`python setup.py install`, run as root.

Dependencies
------------

Juno's only required dependency is [SQLAlchemy][sqlalchemy].

There are a number of optional dependencies:
    
* [Jinja2][jinja2] or [Mako][mako]: Juno has builtin support for these
  templating libraries.  You can use a different one but that will require
  extra configuration.
* [Flup][flup]: Flup is required if you want to use FastCGI or SCGI.
* [Beaker][beaker]: Beaker is required if you want to use sessions.


Server Configuration
----------------------

Juno is set by default to run the builtin development server.  In addition,
it offers interfaces through SCGI, FastCGI, and WSGI.


SCGI Notes
----------

For Nginx, SCGI requires the [mod_scgi][mod_scgi] addon, which is not included 
in the default install.  After installing it, the configuration for Nginx should
look something like this:
    
    http {
        server {
            location / {
                scgi_pass   127.0.0.1:8000;
                include     scgi_vars;
            }
        }
    }

This would be in addition to whatever other options you were setting.

After starting Nginx with those settings, run Juno in 'scgi' mode.


WSGI Notes
----------

Since [mod_wsgi][mod_wsgi] requires a function named 'application', you would
need to put Juno in 'wsgi' mode and call run() like so:
    
    config('mode', 'wsgi')
    application = run()

Those functions will make more sense later.


[sqlalchemy]: http://www.sqlalchemy.org
[jinja2]:     http://jinja.pocoo.org/2/
[mako]:       http://www.makotemplates.org
[flup]:       http://trac.saddi.org/flup/
[beaker]:     http://wiki.pylonshq.com/display/beaker/Home
[mod_scgi]:   http://wiki.codemongers.com/NginxNgxSCGIModule
[mod_wsgi]:   http://code.google.com/p/modwsgi/
