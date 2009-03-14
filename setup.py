from distutils.core import setup
import sys

try:
    import sqlalchemy
except:
    print ''
    print '** SQLAlchemy is required by Juno'
    print '** Download from: http://sqlalchemy.org/download.html'
    print '** Or run: `easy_install SQLAlchemy`'
    print ''
    sys.exit()

try:
    import flup
except:
    print ''
    print '** To use SCGI and FastCGI, Juno requires flup'
    print '** Download from: http://trac.saddi.com/flup/'
    print "** If you\'re not going to use SCGI or FastCGI, ignore this message"
    print ''

try:
    import jinja2
except:
    try:
        import mako
    except:
        print ''
        print '** Juno uses Jinja2 or Mako templates by default'
        print '** Using another template library will require additional configuration'
        print '** Download from: http://pypi.python.org/pypi/Jinja2'
        print '**       or from: http://pypi.python.org/pypi/Mako'
        print '** Alternatively: `easy_install Jinja2`'
        print '**           and: `easy_install Mako`'
        print ''

try:
    import beaker
except:
    print ''
    print '** Beaker is used for Juno\'s session management'
    print '** Download from: http://wiki.pylonshq.com/display/beaker/Home'
    print '** Or run: `easy_install Beaker`'
    print '** If you\'re not going to use sessions, ignore this message.'
    print ''

try:
    import werkzeug
except:
    print ''
    print '** To use the middleware debugger, Juno requires Werkzeug'
    print '** Download from: http://dev.pocoo.org/projects/werkzeug'
    print '** Or run: `easy_install Werkzeug`'
    print '** If you\'re not going to use the debugger, ignore this message.'
    print ''

setup(name         = 'Juno',
      description  = 'A lightweight Python web framework',
      author       = 'Brian Reily',
      author_email = 'brian@brianreily.com',
      url          = 'http://brianreily.com/project/juno/',
      version      = '0.1',
      py_modules   = ['juno'],
      classifiers  = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
      ],
     )
