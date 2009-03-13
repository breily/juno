
Configuration
=============

Start out by importing Juno:
    
    import juno

Juno has a number of configuration options that you can set by calling
init() with a dictionary of settings at the beginning of your application:
    
    juno.init({'config_opt': 'val', 'other_option': 'val2'})

Juno uses a global object to store all of your settings, but you can also
create it directly (it will automatically store it as the global object):
    
    my_juno_object = juno.Juno({'arg': 'val'})

You can access settings later in a number of ways.  If you created a Juno
object yourself, you can access them like so:
    
    my_juno = juno.Juno({'mode': 'wsgi', 'use_sessions': True})
    my_juno.config['mode']  # => 'wsgi'
    my_juno.mode            # => 'wsgi'
    my_juno.use_sessions    # => True

You can also use the config() function to access settings:
    
    juno.init({'template_lib': 'mako'})
    juno.config('template_lib')  # => 'mako'

And set settings:

    juno.config('log')          # => True
    juno.config('log', False)
    juno.config('log')          # => False

A full listing of options:

General Options
---------------

    * 'log': True
      => If True, writes information to stdout during requests.

Types and Encodings
-------------------

    * 'charset': 'utf-8'
      => The default charset encoding used to load and render templates.

    * 'content_type': 'text/html'
      => The default Content-Type header sent in responses.
  
Server Options
--------------

    * 'mode': 'dev'
      => Controls which interface Juno runs - 'dev' runs the development server,
         'scgi' runs the SCGI server, 'fcgi' runs the FastCGI server, and 'wsgi'
         allows you to retrieve an application() object for mod_wsgi.

    * 'scgi_port': 8000
      => The port where the SCGI server runs.

    * 'fcgi_port': 8000
      => The port where the FastCGI server runs.

    * 'dev_port': 8000
      => The port where the development server runs.

Static File Options
-------------------

    * 'use_static': True
      => If True, Juno sets up a static file handler for you.

    * 'static_url': '/static/*:file/'
      => The URL that is mapped to the static handler.  For example, matches
         '/static/stylesheet.css'.

    * 'static_root': './static/'
      => The filesystem path where static files are loaded from.  '/static/file.css'
         by default will map to './static/file.css' on your system.

    * 'static_handler': static_serve
      => The function that serves static files.

Template Options
----------------

    * 'use_templates': True
      => If True, set up templates.

    * 'template_lib': 'jinja2'
      => Juno has built-in template configurations for Jinja2 and Mako ('mako').

    * 'get_template_handler': _get_template_handler
      => The function Juno calls when you load a template with template().

    * 'render_template_handler': _render_template_handler
      => The function Juno calls when template() renders a template.

    * 'auto_reload_templates': True
      => If True, templates are automatically reloaded when they change.

    * 'translations': []
      => A list of translation objects to be passed to Jinja2's i18n extension.
         A translation object is one returned by gettext.translation or the
         equivalent.  If the list is empty, the i18n extension is not enabled.
         This option only acts on Jinja2 currently.

    * 'template_kwargs': {}
      => Allows you to pass custom keyword arguments to the template lookup
         object (Environment for Jinja2, TemplateLookup for Mako).

    * 'template_root': './templates/'
      => The filesystem path where templates are loaded from.

    * '404_template': '404.html'
      => The template to load when no matching URL is found for a request.

    * '500_template': '500.html'
      => The template to load when an error occurs during a request.

Database Options
----------------

    * 'use_db': True
      => If True, a connection to a database is setup.  Even if this value is False,
         SQLAlchemy is currently still imported and thus required.

    * 'db_type': 'sqlite'
      => The type of database driver to use.  Can be 'sqlite', 'postgres',
         'mysql', 'oracle', or 'mssql'.

    * 'db_location': ':memory:'
      => The location/address of your database. Read the SQLAlchemy docs
         (http://www.sqlalchemy.org/docs/05/dbengine.html#create-engine-url-arguments)
         for details.

Custom Middleware
-----------------

    * 'middleware': []
      => The list of custom WSGI middleware you want your application to be
         wrapped in. Each entry in the list should be a tuple in the following
         format:

         ('package.name.Middleware', {'arg': 'value'})

Session Options
---------------

    * 'use_sessions': False
      => If True, Juno will set up and use sessions.

    * 'session_lib': 'beaker'
      => The library to use for sessions.  Currently 'beaker' is the only option.

Debugger Options
----------------

    * 'use_debugger': False
      => If True, Juno will set up the default debugging middleware.

    * 'raise_view_exceptions': False
      => If True, uncaught exceptions during a request will be propagated.
         You'll need to set this to True if you want to use a custom debugging
         middleware.


[dbdocs]: 
