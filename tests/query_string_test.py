import juno

init({'use_db': False, 'use_templates': False, 'use_static': False,
      'mode': 'wsgi',

@juno.get('/')
def index(web):
    ret = ''
    for k, v in web.input().items():
        ret += '%s: %s\t' % (k, v)
    return ret

application = run()
