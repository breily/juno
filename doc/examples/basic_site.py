#
# This Juno application runs my site (http://brianreily.com).
# 
# It has been modified for added comments and improved readability.
# If you are interested in the full project for this site (i.e. with
# templates, static file setup, etc.), see my Github repository for it:
# http://github.com/breily/brianreily.com
#

from juno import *

# Initialize the database, and set Juno to run the SCGI server
init({'db_location': 'brian.db', 'mode': 'scgi'})

# Represents software with READMEs/repositories
Project = model('Project', name     = 'string', 
                           about    = 'string',     # Short description
                           readme   = 'string',     # Location of the README
                           repo     = 'string',     # URL of Github repository
                           status   = 'int',        # Current/Completed/Old
                           # Replace the built in __repr__ with a more
                           # descriptive version of it.
                           __repr__ = lambda self: '<Project: %s>' %self.name)

# Represents shorter pieces of code (without READMEs/repositories)
Code = model('Code', name     = 'string', 
                     about    = 'string',   # Short description
                     gist_id  = 'int',      # ID of the Github Gist
                     __repr__ = lambda self: '<Code: %s>' %self.name)

# Redirect these two URLs to the home page; I didn't want separate list pages
assign(['/project/', '/code/'], '/')

# The home page - lists all Project and Code items
@get('/')
def home(web):
    projects = find(Project).all()  # Retrieve Project items
    code = find(Code).all()         # Retrieve Code items
    # Render the main template, while splitting Projects based on status
    template('main.html', {
        'current_projects':    [p for p in projects if p.status == 0],
        'complete_projects':   [p for p in projects if p.status == 1],
        'incomplete_projects': [p for p in projects if p.status == 2],
        'code':                code
    })

# Currently checks for Project existence and returns the README
@get('/project/:name/')
def project(web, name):
    # Check if a project with a similar/same name exists
    # This just uses SQLAlchemy's filter() function
    proj = find(Project).filter(Project.name.like('%' + name + '%')).all()
    # If not found, return a 404
    if len(proj) == 0: return notfound("That Project (%s) cannot be found" %name)
    # Return the README file, as plain text
    yield_file(proj[0].readme, type='text/plain')

# Currently checks for Code existence, and renders the generic Code template
@get('/code/:name/')
def code(web, name):
    # Same as in project function
    c = find(Code).filter(Code.name.like('%' + name + '%')).all()
    if len(c) == 0: return notfound("That Code (%s) cannot be found" %name)
    # Render the generic code template (which has javascript to insert the Gist)
    template('code.html', { 'c': c[0] })

# Run Juno
if __name__ == '__main__': run()
