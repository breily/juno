from juno import *

# Expected result after submitting:
#     web.input() = {'input1': 'value1'}
@route('/simple-get-form')
def simple_get_form(web):
    return """<html><head></head><body>
        <form method="GET">
        <input type="text" name="input1" value="value1" />
        <input type="submit" />
        </form>""" + "web.input() = " + str(web.input()) + "</body></html>";


# Expected result after submitting:
#     web.input() = {'input1': 'value1'}
@route('/simple-post-form')
def simple_post_form(web):
    return """<html><head></head><body>
        <form method="POST">
        <input type="text" name="input1" value="value1" />
        <input type="submit" />
        </form>""" + "web.input() = " + str(web.input()) + "</body></html>";


# Expected result after submitting:
#     web.input() = {'query1': 'qvalue1', 'input1': ['qvalue2', 'value1']}
@route('/post-form-with-query-params')
def post_form_with_query_params(web):
    return """<html><head></head><body>
        <form method="POST" action="?query1=qvalue1&amp;input1=qvalue2">
        <input type="text" name="input1" value="value1" />
        <input type="submit" />
        </form>""" + "web.input() = " + str(web.input()) + "</body></html>";


# Expected result after submitting:
#     web.input() = {}
@route('/empty-upload-form')
def empty_upload_form(web):
    return """<html><head></head><body>
        <form method="POST" enctype="multipart/form-data" action="">
        <input type="submit" />
        </form>""" + "web.input() = " + str(web.input()) + "</body></html>";


# Expected result after submitting:
#     web.input() = {'file1': cgi.FieldStorage('file1', ...), 'input1': 'value1'}
# or
#     web.input() = {'file1': '', 'input1: 'value1'} -- if no file was selected
@route('/simple-upload-form')
def simple_upload_form(web):
    return """<html><head></head><body>
        <form method="POST" enctype="multipart/form-data" action="">
        <input type="file" name="file1" />
        <input type="text" name="input1" value="value1" />
        <input type="submit" />
        </form>""" + "web.input() = " + str(web.input()) + "</body></html>";


# Expected result after submitting:
#     web.input() = {
#         'qinput1': 'qvalue1',
#         'file1': ['qvalue2',
#                   'notafile1',
#                   cgi.FieldStorage('file1', ...),
#                   cgi.FieldStorage('file1', ...),
#                   'notafile2'],
#         'file2': cgi.FieldStorage('file2', ...),
#         'input1': ['value2_1', 'value2_2']
#     }
@route('/upload-form')
def upload_form(web):
    return """<html><head></head><body>
        <form method="POST" enctype="multipart/form-data" action="?qinput1=qvalue1&amp;file1=qvalue2">
        <input type="text" name="file1" value="notafile1" />
        <input type="file" name="file1" />
        <input type="file" name="file1" />
        <input type="file" name="file2" />
        <input type="text" name="input1" value="value1_1" />
        <input type="text" name="input1" value="value1_2" />
        <input type="text" name="file1" value="notafile2" />
        <input type="submit" />
        </form>""" + "web.input() = " + str(web.input()) + "</body></html>";


if __name__ == '__main__':
    run()
