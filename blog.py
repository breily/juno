from juno import *
from data import Project, session

@get('/')
def home(web):
    projects = session.query(Project).all()
    html().head().title('projects').endhead().body()
    for project in projects:
        div().text('%s: %s' %(project.name, project.description)).enddiv()
    endbody().endhtml()

@get('/project/*:name/')
def project(web, name):
    project = session.query(Project).filter(Project.name.like(name)).one()

if __name__ == '__main__': run()
