from distutils.core import setup
import sys

try:
    import sqlalchemy
except:
    print '** SQLAlchemy is required by Juno'
    print '** Download from: http://sqlalchemy.org/download.html'
    print '** Or run: `easy_install SQLAlchemy`'
    sys.exit()

try:
    import flup
except:
    print '** To use SCGI, Juno requires flup'
    print '** Download from: http://trac.saddi.com/flup/'
    print "** If you don't want SCGI, disregard this message"

try:
    import jinja2
except:
    print '** Jinja2 templates are the default templates for Juno'
    print '** Download from: http://pypi.python.org/pypi/Jinja2'
    print '** Or run: `easy_install Jinja2`'
    print '** Again, Jinja2 is not required.'

setup(name         = 'juno',
      description  = 'A lightweight Python web framework',
      author       = 'Brian Reily',
      author_email = 'brian@brianreily.com',
      url          = 'http://brianreily.com/project/juno/',
      version      = '0.1',
      py_modules   = ['juno'],
     )
