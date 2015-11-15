# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

import datetime

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    #response.flash = T("Hello World")
    if auth.user :
        redirect("home")
    message="Welcome to Edify!"
    return locals()#dict(message=T('Welcome to web2py!'))

@auth.requires_login()
def admin():
    if auth.user.role != 'Admin':
        redirect("home")
    user_table = None
    course_table = None
    verify_grid = None
    rows = None
    if request.args(0) == "auth_user":
        user_table = SQLFORM.smartgrid(db.auth_user)
    elif request.args(0) == "course":
        course_table = SQLFORM.smartgrid(db.course)
    elif request.args(0) == "verify_faculty":
        query = (db.auth_user.admin_verified == 'no')&(db.auth_user.role == 'faculty')       
        #verify_grid = SQLFORM.smartgrid(db.auth_user, constraints = dict(auth_user=query))
        verify_grid = 12
        rows = db(query).select()
        if(len(rows) == 0):
            verify_grid = -1
        else:
            verify_grid = len(rows)
    return locals()

@auth.requires_login()
def admin_verify():
    if auth.user.role != 'Admin' or request.args(0) == None:
        redirect("home")
    user1_id = request.args(0)
    row = db(db.auth_user.id == user1_id).select()
    if len(row) == 0:
        response.flash = "Invalid user"
    else :
        db(db.auth_user.id == user1_id).update(admin_verified='yes')
        
        #redirect("admin");
    response.template = "admin"
    s = str(len(row))
    response.flash = s
    redirect(URL("default","admin/verify_faculty"))
    return locals()



@auth.requires_login()
def home():
    message = None
    auth_error = None
    courses = None
    my_courses = None
    user_id = auth.user.id
    rows = db( (db.auth_user.id == user_id) & (db.auth_user.admin_verified == 'no') & (db.auth_user.role == 'faculty') ).select()
    if(len(rows) == 1):
        auth_error = "You are still awaiting faculty status approval, contact admin for more details "
    else:
        message = "Welcome, "+auth.user.first_name        
        if auth.user.role == 'faculty':
            courses = db(db.course.faculty == user_id).select()
            courses_undertaken = db(db.course.faculty == auth.user.id).select()
            course_id_set = set( [i.id for i in courses_undertaken] )    

            if len(course_id_set)!=0:
                activities = db((db.activity.activity_scope == 'all') & (db.activity.cid.belongs(course_id_set))).select(orderby=~db.activity.publish_date)
            else :
                activities = []
        else:
            my_courses = db((db.course_registration.sid == user_id)).select()            
            my_ta_courses = db(db.course_ta.sid == user_id).select()
            course_ids = set([ i.cid for i in my_courses ])            
            if(len(my_ta_courses) != 0):
                for i in my_ta_courses:
                    course_ids.add(i.cid)
                activities = db((db.activity.activity_scope.belongs('all','ta')) & (db.activity.cid.belongs(course_ids))).select(orderby=~db.activity.publish_date)
            else:
                activities = db((db.activity.activity_scope == 'all') & (db.activity.cid.belongs(course_ids))).select(orderby=~db.activity.publish_date)    
            
            #activities = db((db.activity.activity_scope == 'all') & (db.activity.cid.belongs(course_ids))).select()
            dead_lines = db((db.course_assignments.deadline >= datetime.datetime.now()) & (db.course_assignments.cid.belongs(course_ids))).select()
    return locals()    

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    #if request.args(0) == 'register':

    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


