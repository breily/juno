from juno import Juno, JunoResponse

def index(request):
    body = '''
        <html>
            <head>
                <title>index</title>
            </head>
            <body>
                index
            </body>
        </html>'''
    return JunoResponse(body, '200')

def hello(request):
    return '<html>hello there</html>'

urls = [
    ['/', index],
    ['/hello', hello],
       ]
