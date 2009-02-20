from juno import *

Person = model('Person', name='str', views='int')

@route('/makeperson/*:name/')
def makeperson(web, name):
    exist = Person.find().filter(Person.name==name)
    if exist.count() != 0: return 'That person already exists'
    p = Person(name=name, views=0).save()
    return 'Person created'

@route('/getperson/*:name/')
def getperson(web, name):
    exist = Person.find().filter(Person.name==name).all()
    if len(exist) == 0: return 'That person does not exist'
    p = exist[0]
    p.views += 1
    p.save()
    return 'You have viewed this person %s time(s)' % p.views

run()
