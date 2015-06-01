
Juno Template API
====================

Basics
--------

Juno is enabled by default to use Jinja2 templates.  Juno can also use
Mako template by changing 'template_lib':
    
    init({'template_lib': 'mako'})

If you are using either Jinja2 or Mako, you can skip the next section.


Changing Template Engines
---------------------------

Juno can use any templating system that has some sort of template
object that can be specified by name and some way to return a string 
version of that object - i.e. Jinja2 has Template objects loaded from 
the filesystem, and has a render() method to return a string of that
file.

To start, change the 'template_lib' option to something other than
'jinja2' or 'mako':
    
    config('template_lib', 'my_template_lib')

Then you have to give Juno two functions - 'get_template_handler' and
'render_template_handler'.  The first takes a string (most often a
filename) and must return an object that can be rendered (i.e. the
Template objects in Jinja2 and Mako).  The second function takes a 
template object and a dictionary of keyword arguments (**kwargs).
It must return a string.

As an example, here is how Juno sets this up for Jinja2 (Jinja2's
environment object is stored in config('my_jinja_environ'):
    
    def get_template_handler(path):
        return config('my_jinja_environ').get_template(path)

    def render_template_handler(template_obj, **kwargs):
        return template_obj.render(**kwargs)

    config('get_template_handler', get_template_handler)
    config('render_template_handler', render_template_handler)


Rendering
-----------

To render a template (adds the rendering to the current response object):

    template('index.html')

To render a template with variables, you can use a dictionary or named
parameters:
    
    template('index.html', {'foo': 1, 'bar': 2})
    template('index.html', foo=1, bar=2)

You can also set a template to automatically render for a given url:
    
    autotemplate('/', 'index.html')
    autotemplate(['/index/', '/home/'], 'home.html')

Currently, this does not accept any arguments in the url.


Template Objects
------------------

If you want to retrieve a template object without rendering it, you
can use the function get_template:
    
    template_obj = get_template('index.html')

Before returning this you would need to render and add it to the 
response.

