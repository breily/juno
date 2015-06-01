Using Forms in Juno
======================

Suppose you have a form:
    
    <form action='/submit/' method='post'>
        <input type='text' name='email' />
        <input type='submit' />
    </form>

In the view assigned to '/submit/', you can access the form elements using:
    
    web.input()         # => {'email': 'brian@brianreily.com'}
    web.input('email')  # => 'brian@brianreily.com'

This works the same for all form elements, as well as query strings.

In case of an uploaded file web.input returns a cgi.FieldStorage instance
instead of a string. Examples of processing a file element:

    f = web.input('file_field') # => the cgi.FieldStorage instance for the file
    f.file # => a file(-like) object that you can use to read data from the uploaded file

You can also use the value attribute of the cgi.FieldStorage instance but be aware
that it reads the file every time you request the value.

    f = web.input('file_field')
    f.value # => string holding the contents of the file
