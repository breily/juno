
Juno Model API
=================

Juno's model API is a little different than most other frameworks as 
you don't use Python's class keyword, but instead simply call Juno's
model function.  A simple example:
    
    Person = juno.model('Person', name='string')

Person is now a class that you can use to construct objects, just as if
you had used `class Person:`.  The `name='string'` portion creates an
instance variable called `name` and maps it to a SQLAlchemy column of 
type String.

To instantiate a Person object, you must use keyword arguments:
    
    brian = Person(name='brian')

`brian` now has a `name` variable and an `id` variable (its database 
primary key).  It also has the following methods:

    brian.add()         # Adds the object to the current session, but
                        # doesn't commit it.
    brian.save()        # Adds (if necessary) and commits the object.
    brian.__repr__()    # Defaults to '<Person: id = X>'


Adding Other Database Columns
-------------------------------

You can add database columns by using string versions of their SQLAlchemy
column names ('string' for String).  You can also pass in literal Column
objects (see the SQLAlchemy docs for information on those):
    
    Person = juno.model('Person', name=Column(String))


Adding Custom Functions
-------------------------

You can add custom functions to your model in the model(...) call.  For
example, to add your own `__repr__`, use something like the following:
    
    Person = juno.model('Person', name='string',
        __repr__=lambda self: '<Person: %s>' %self.name)

You could also define the function beforehand if you needed more than one
statement, or don't like lambdas:
    
    def my_repr(self): return '<Person: %s>' %self.name

    Person = juno.model('Person', name='string', __repr__=my_repr)


Querying for Objects
----------------------

Juno doesn't have its own query language, and instead just gives you access
to SQLAlchemy's query system.  To use it, use the find function and then 
attach whatever SQLAlchemy methods you need:

    people = juno.find(Person).all()

Models also include a find() function:
    
    people = Person.find().all()


Other Notes
-------------

If you need to use the current session directly, use the session() function,
which returns the SQLAlchemy session object:
    
    session().add_all([Person(...), Person(...), ...])


Creating a Database Connection
--------------------------------

Juno's default database engine is an in-memory SQLite database.  To specify
something different, use the 'db_type' and 'db_location' settings by calling
init() after importing Juno:
    
    juno.init({'db_type': 'mysql', 'db_location': 'localhost/foo'})

The database type can be any of the drivers that SQLAlchemy supports, and
the location is the part of the engine URL after the 'driver://' part.
See http://www.sqlalchemy.org/docs/05/dbengine.html#create-engine-url-arguments
for details.


For the Curious: How the Model Function Works
-----------------------------------------------

Juno's model() function is a little strange in that it is a normal function
that returns a class, exactly the same as if you had used the `class` keyword
to define it.  This is possible because of Python's metaclasses - classes
whose instances are classes.  In juno.py, JunoClassConstructor subclasses
'type', a builtin Python metaclass.  This allows model() to return a class
instead of a normal instance.

So how does your class get the variables and methods you want?  model()
takes the parameters you passed in (name='string') and builds a dictionary
that maps variable names ('name') to the database column you specified
(Column('name', String)).  Then it adds any callables you gave it (like the
`__repr__` example above), and then adds the included methods (default `__repr__`,
generic `__init__`, etc.).

This dictionary is passed along with your class name to the class constructor
mentioned above, and your class comes back out, and returned to you.


Reference
-----------

juno.model(class_name, variable_name=column_type, ..., callables)

    > Returns a class with the given variable names and methods.
    > By default includes:
        id       => Integer database column (primary key)
        __init__ => Functions like a normal __init__, and just like a 
                    normal class you don't call it directly.
        __repr__ => Returns '<class_name: id = id>'
        add      => Adds instance to current session.
        save     => Adds and commits instance.
        find     => Class method to return a Query object.
    > Column types are all lowercase versions of the standard SQLAlchemy
      types ('string', 'integer', 'unicode', 'text', 'unicodetext', 'date',
      'numeric', 'time', 'float', 'datetime', 'interval', 'binary', 'boolean',
      'pickletype'), or actual Column objects.  See SQLAlchemy reference for 
      details.
    > Callables are any lambdas or normal functions you want your class
      to have.  Like normal methods, they must take self as their first
      parameter (see __repr__ example).

juno.find(class or class_name)

    > Returns a SQLAlchemy query object for that model.
    > Takes a single parameter, which can either be a class or a string
      name of one (Person or 'Person').
    > This is the same as Person.find()
