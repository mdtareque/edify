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
        redirect(URL("default","home"))
    message="Welcome to Edify!"
    return locals()#dict(message=T('Welcome to web2py!'))

@auth.requires_login()
def admin():
    if auth.user.role != 'Admin':
        redirect("home")
    user_table = None
    course_table = None
    course_ta_table = None
    course_registration_table = None
    course_resources_table = None
    course_assignments_table = None
    course_assignment_upload_table = None
    activity_table= None
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
    elif request.args(0) == "course_ta":
        course_ta_table = SQLFORM.smartgrid(db.course_ta)
    elif request.args(0) == "course_registration":
        course_registration_table = SQLFORM.smartgrid(db.course_registration)
    elif request.args(0) == "course_resources":
        course_resources_table = SQLFORM.smartgrid(db.course_resources)
    elif request.args(0) == "course_assignments":
        course_assignments_table = SQLFORM.smartgrid(db.course_assignments)
    elif request.args(0) == "course_assignment_upload":
        course_assignment_upload_table = SQLFORM.smartgrid(db.course_assignment_upload)
    elif request.args(0) == "activity":
        activity_table = SQLFORM.smartgrid(db.activity)

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
    imp_dates = []  # to be populated from a table
    # obj = [
    # (T('Home2'), False, URL('default', 'index'), []),
    # (T('Courses2'), False, URL('course', 'index'), [])
    # ]
    #{{response.menu.extend(obj)}}
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
                activities = db((db.activity.activity_scope.belongs(('all','faculty'))) & (db.activity.cid.belongs(course_id_set))).select(orderby=~db.activity.publish_date,limitby=(0, 10))
            else :
                activities = []
        else:
            my_courses = db((db.course_registration.sid == user_id)).select()
            my_ta_courses = db((db.course_ta.sid == user_id)).select()
            course_ids = set([ i.cid for i in my_courses ])
            if(len(my_ta_courses) != 0):
                my_ta_courses2 = db((db.course_ta.sid == user_id) & (db.course_ta.approval == 'yes')).select()
                ta_course_ids = set()
                for i in my_ta_courses2:
                    ta_course_ids.add(i.cid)
                query1  = ((db.activity.activity_scope.belongs(['all']) ) & (db.activity.cid.belongs(course_ids)))
                query3 = ((db.activity.activity_scope.belongs(['ta','all']) ) & (db.activity.cid.belongs(ta_course_ids)))
                query2 = ((db.activity.activity_scope.belongs(['student']) )& (db.activity.sid == auth.user.id))
                activities = db(query1 | query2 | query3 ).select(orderby=~db.activity.publish_date,limitby=(0, 10))
                #activities = db(query1).select(orderby=~db.activity.publish_date,limitby=(0, 10))
                #activities2 = db(query2).select(orderby=~db.activity.publish_date,limitby=(0, 10))
                #activities = activities | activities2

            else:
                query1  = (db.activity.activity_scope.belongs(['all']) ) & (db.activity.cid.belongs(course_ids))
                query2 = (db.activity.activity_scope.belongs(['student']) )& (db.activity.sid == auth.user.id)
                activities = db(query1 | query2).select(orderby=~db.activity.publish_date,limitby=(0, 10))
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
    auth.settings.mailer = mail
    if request.args(0) == 'profile':
        redirect(URL("default","profile"))
    return dict(form=auth())

def register():

    def validate_email(form):
        email_id = form.vars.email
        at_i = email_id.find("@")
        dom = email_id[at_i:]
        if(dom != "@students.iiit.ac.in"):
            form.errors["email"] = "Invalid email: only students mail id's are accepted"
    auth.settings.register_onvalidation.append(validate_email)
    form=auth.register()
    return locals()

@auth.requires_login()
def profile():
    db.auth_user.role.readable =False
    db.auth_user.role.writable = False
    db.auth_user.email.readable =False
    db.auth_user.email.writable = False
    db.auth_user.admin_verified.readable =False
    db.auth_user.admin_verified.writable = False
    form=auth.profile()
    return locals()

@auth.requires_login()
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
