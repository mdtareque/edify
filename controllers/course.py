import time

POST_PER_PAGE=6

@auth.requires_login()
def index():
#list the courses available for current year for registration
    courses = []
    page = request.args(0, cast=int, default=0)
    start = page*POST_PER_PAGE
    stop = start + POST_PER_PAGE
    rows = db(db.course).select(limitby=(start, stop))
    for row in rows:
      courses.append([row.name, row.faculty.first_name + " " +  row.faculty.last_name, row.id])
    return locals()

@auth.requires_login()
def index_search():
    courses = []
    page = request.args(0, cast=int, default=0)
    start = page*POST_PER_PAGE
    stop = start + POST_PER_PAGE
    search_query = request.vars.search_courses
    rows = db(db.course.name.like('%'+search_query+'%')).select(limitby=(start, stop))
    for row in rows:
        courses.append([row.name, row.faculty.first_name + " " +  row.faculty.last_name, row.id])
    return locals()

# @auth.requires_login()
# def index():
# 	#list the courses available for current year for registration
# 	courses = []
# 	rows = db(db.course).select()
# 	for row in rows:
# 		courses.append([row.name, row.faculty.first_name + " " +  row.faculty.last_name, row.id])
# 	return locals()

@auth.requires_login()
def view():
	course_id = request.args(0)
	rows = db(db.course.id ==course_id).select()
	#faculty = None
	if(len(rows) == 0):
		response.flash = "Invalid course"
	else:
		message = rows[0].name
		faculty = rows[0].faculty.first_name + " " + rows[0].faculty.last_name
		course_description = rows[0].course_description
		rows = db((db.course_registration.cid==course_id)&(db.course_registration.sid==auth.user.id)).select()
		if len(rows) == 0:
			registered = 0
		else:
			registered = 1
		rows = db((db.course_ta.cid==course_id)&(db.course_ta.sid==auth.user.id)).select()
		if len(rows) == 0:
			is_ta = 0
		else:
			is_ta = 1	
	return locals()

@auth.requires_login()
def register():
	course_id = request.args(0)
	rows = db(db.course.id ==course_id).select()
	#faculty = None
	if(len(rows) == 0):
		response.flash = "Invalid course"
	else:
		db.course_registration.insert(cid=course_id, sid=auth.user.id)
		db.activity.insert(cid=course_id, sid=auth.user.id, 
			description="You registered for "+course[0].name+" course.",
			activity_scope="student"
			)
		redirect(URL("course","main/"+str(course_id)))
	return locals()
		
@auth.requires_login()
def unregister():
	course_id = request.args(0)
	rows = db(db.course.id ==course_id).select()
	if(len(rows) == 0):
		response.flash = "Invalid course"
	else:
		db((db.course_registration.cid==course_id)&(db.course_registration.sid==auth.user.id)).delete()
		redirect(URL("course","main/"+str(course_id)))
	return locals()

@auth.requires_login()
def ta_register():
	course_id = request.args(0)
	rows = db(db.course.id ==course_id).select()
	#faculty = None
	if(len(rows) == 0):
		response.flash = "Invalid course"
	else:
		db.course_ta.insert(cid=course_id, sid=auth.user.id)
		#adding activity
		db.activity.insert(cid=course_id, sid=auth.user.id, 
			description=auth.user.first_name+" "+auth.user.last_name+" requested for TAship for "+rows[0].name+" course.",
			activity_scope="faculty"
			)
		redirect(URL("course","main/"+str(course_id)))
	return locals()
		
@auth.requires_login()
def ta_unregister():
	course_id = request.args(0)
	rows = db(db.course.id ==course_id).select()
	if(len(rows) == 0):
		response.flash = "Invalid course"
	else:
		db((db.course_ta.cid==course_id)&(db.course_ta.sid==auth.user.id)).delete()
		redirect(URL("course","main/"+str(course_id)))
	return locals()

@auth.requires_login()
def manage_course():
	course_id = request.args(0)	
	ta_requests = db((db.course_ta.cid == course_id)&(db.course_ta.approval == 'no')).select()
	course_ta   = db((db.course_ta.cid == course_id)&(db.course_ta.approval == 'yes')).select()
	if(len(ta_requests) == 0):
		courses = db(db.course.id == course_id).select()
		message = courses[0].name#response.flash = "Invalid course"
	else:
		message = ta_requests[0].cid.name
	return locals()

@auth.requires_login()
def main():
	course_id = request.args(0)
	rows = db(db.course.id ==course_id).select()
	if(len(rows) == 0):
		response.flash = "Invalid course"
	else:
		message = rows[0].name
		faculty = rows[0].faculty
		instructor = rows[0].faculty.first_name + " " + rows[0].faculty.last_name
		course_description = rows[0].course_description
		rows = db((db.course_registration.cid==course_id)&(db.course_registration.sid==auth.user.id)).select()
		if len(rows) == 0:
			registered = 0			
		else:
			registered = 1
		rows = db((db.course_ta.cid==course_id)&(db.course_ta.sid==auth.user.id)).select()
		if len(rows) == 0:
			is_ta = 0
		else:
			is_ta = 1
		rows = db((db.course_ta.cid==course_id)&(db.course_ta.sid==auth.user.id)&(db.course_ta.approval == 'yes')).select() 
		if( len(rows) == 1):
			ta_approved = 1
		else:
			ta_approved = 0
		# if( registered == 0 and is_ta == 0 and faculty != auth.user.id):
		# 	redirect(URL("default","index"))
		tas = db((db.course_ta.cid == course_id)&(db.course_ta.approval == 'yes')).select()
	return locals()

@auth.requires_login()
def approve_ta():
	ta_id =request.args(0)
	ta_requests = db((db.course_ta.id == ta_id)).select()
	if(len(ta_requests) == 0):
		response.flash = "Invalid TA"
	else:
		db((db.course_ta.id == ta_id)).update(approval='yes')
		db.activity.insert(cid=ta_requests[0].cid, sid=auth.user.id, 
			description=auth.user.first_name+" "+auth.user.last_name+" approved your TAship request for "+ta_requests[0].cid.name+" course.",
			activity_scope="ta"
			)
		redirect(URL("course","main/"+str(ta_requests[0].cid)))
	return locals()

@auth.requires_login()
def reject_ta():
	ta_id =request.args(0)
	ta_requests = db((db.course_ta.id == ta_id)).select()
	if(len(ta_requests) == 0):
		response.flash = "Invalid TA"
	else:
		db((db.course_ta.id == ta_id)).delete()
		db.activity.insert(cid=ta_requests[0].cid, sid=auth.user.id, 
			description=auth.user.first_name+" "+auth.user.last_name+" rejected your TAship request for "+ta_requests[0].cid.name+" course.",
			activity_scope="ta"
			)
		redirect(URL("course","main/"+str(ta_requests[0].cid)))
	return locals()

@auth.requires_login()
def home():
	course_id = request.args(0)
	course = db(db.course.id == course_id).select()
	if(course and len(course) == 1):
		course_des = course[0].course_description				
	else:
		response.flash = "Invalid course" 
	return locals()

@auth.requires_login()
def assignments():
	course_id = request.args(0)
	course = db(db.course.id == course_id).select()
	is_staff = 0
	if(len(course) == 0):
		response.flash = "Invalid course" 
	else:
		if course[0].faculty == auth.user.id:
			is_staff = 1
		else:			
			ta_approved = db((db.course_ta.cid == course_id)&(db.course_ta.sid == auth.user.id)&(db.course_ta.approval=='yes')).select()			
			if len(ta_approved) == 1:
				ta_approved = 1
			else:
				ta_approved = 0
		links = db(db.course_assignments.cid==course_id).select()				
	return locals()

@auth.requires_login()
def upload_assignment():
	data = request.vars
	course_id = request.args(0)
	course = db(db.course.id == course_id).select()
	if(len(course) == 0):
		response.flash = "Invalid course" 
	else:
		data = request.vars
		db.course_assignments.insert(cid=course_id,sid=auth.user.id,attachment=data.assignment_file, title=data.assignment_name, deadline=data.assignment_deadline, total_marks=data.assignment_total_marks)			
		db.activity.insert(cid=course_id, sid=auth.user.id, 
			description=auth.user.first_name+" "+auth.user.last_name+" uploaded new assignment, \""+data.assignment_name+"\" for "+course[0].name+" course.",
			activity_scope="all"
			)
	redirect(URL('course','main/'+str(course_id)))
	return locals()

@auth.requires_login()
def upload_resource():
	data = request.vars
	course_id = request.args(0)
	course = db(db.course.id == course_id).select()
	if(len(course) == 0):
		response.flash = "Invalid course" 
	else:
		data = request.vars
		db.course_resources.insert(cid=course_id,sid=auth.user.id,attachment=data.resource_file, title=data.resource_name)			
		db.activity.insert(cid=course_id, sid=auth.user.id, 
			description=auth.user.first_name+" "+auth.user.last_name+" uploaded new resource, \""+data.resource_name+"\" for "+course[0].name+" course.",
			activity_scope="all"
			)
	redirect(URL('course','main/'+str(course_id)))
	return locals()

@auth.requires_login()
def resources():
	course_id = request.args(0)
	course = db(db.course.id == course_id).select()
	is_staff = 0
	if(len(course) == 0):
		response.flash = "Invalid course" 
	else:
		if course[0].faculty == auth.user.id:
			is_staff = 1
		else:
			ta_approved = db((db.course_ta.cid == course_id)&(db.course_ta.sid == auth.user.id)&(db.course_ta.approval=='yes')).select()			
			if len(ta_approved) == 1:
				ta_approved = 1
			else:	
				ta_approved = 0
		links = db(db.course_resources.cid==course_id).select()				
	return locals()

@auth.requires_login()
def upload():
	course_id = request.args(0)
	course = db(db.course.id == course_id).select()
	if(len(course) == 0):
		response.flash = "Invalid course"
	return locals()

@auth.requires_login()
def marks():
	course_id = request.args(0)
	course = db(db.course.id == course_id).select()
	if(len(course) == 0):
		response.flash = "Invalid course"
	return locals()


@auth.requires_login()
def activity():
	course_id = request.args(0)
	course = db(db.course.id == course_id).select()
	if(len(course) == 0):
		response.flash = "Invalid course"
	else:
		activities = db((db.activity.cid==course_id)&(db.activity.activity_scope=='all')).select()
	return locals()


@auth.requires_login()
def approvals():
	course_id = request.args(0)
	course = db(db.course.id == course_id).select()
	if(len(course) == 0):
		response.flash = "Invalid course"
	else:
		ta_requests = db((db.course_ta.cid == course_id)&(db.course_ta.approval == 'no')).select()
		course_ta   = db((db.course_ta.cid == course_id)&(db.course_ta.approval == 'yes')).select()		
	return locals()

@auth.requires_login()
def delete_assignment():
	assignment_id = request.args(0)
	assignment_id = request.args(1)
	assignment = db(db.course_assignments.id == assignment_id).select()
	if( len(assignment) == 0):
		response.flash = "Invalid assignment"
	else:
		db(db.course_assignments.id == assignment_id).delete()
		redirect(URL('course','main/'+str(course_id)))

