import time,datetime

POST_PER_PAGE=6

@auth.requires_login()
def index():
#list the courses available for current year for registration
    courses = []
    page = request.args(0, cast=int, default=0)
    start = page*POST_PER_PAGE
    stop = start + POST_PER_PAGE
    rows = db(db.course).select(limitby=(start, stop))
    count = len(db(db.course).select())
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
    count = len(db(db.course.name.like('%'+search_query+'%')).select())
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
			description="You registered for "+rows[0].name+" course.",
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
		db.activity.insert(cid=course_id, sid=auth.user.id,
			description="You left "+rows[0].name+" course.",
			activity_scope="student"
			)
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
		db.activity.insert(cid=course_id, sid=auth.user.id,
			description="You requested for TAship for "+rows[0].name+" course.",
			activity_scope="student"
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
		db.activity.insert(cid=course_id, sid=auth.user.id,
			description=auth.user.first_name+" "+auth.user.last_name+" left TAship for "+rows[0].name+" course.",
			activity_scope="faculty"
			)
		db.activity.insert(cid=course_id, sid=auth.user.id,
			description="You left TAship for "+rows[0].name+" course.",
			activity_scope="student"
			)
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
		has_edit_access = 0
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
		rows = db((db.course_ta.cid==course_id)&(db.course_ta.sid==auth.user.id)&(db.course_ta.approval=='yes')).select()
		if len(rows) == 0:
			is_ta_approved = 0
		else:
			is_ta_approved = 1
			has_edit_access = 1
		rows = db((db.course_ta.cid==course_id)&(db.course_ta.sid==auth.user.id)&(db.course_ta.approval == 'yes')).select()
		if( len(rows) == 1):
			ta_approved = 1
		else:
			ta_approved = 0
		if faculty == auth.user.id:
			has_edit_access = 1

		# if( registered == 0 and is_ta == 0 and faculty != auth.user.id):
		# 	redirect(URL("default","index"))
		tas = db((db.course_ta.cid == course_id)&(db.course_ta.approval == 'yes')).select()
	return locals()

@auth.requires_login()
def approve_ta():
	if auth.user.role != "faculty":
		return "invalid request"
	ta_id =request.args(0)
	ta_requests = db((db.course_ta.id == ta_id)).select()
	if(len(ta_requests) == 0):
		session.flash = "Invalid TA"
	else:
		db((db.course_ta.id == ta_id)).update(approval='yes')
		db.activity.insert(cid=ta_requests[0].cid, sid=auth.user.id,
			description=auth.user.first_name+" "+auth.user.last_name+" approved TAship request of "+ta_requests[0].sid.first_name+" "+ta_requests[0].sid.last_name+" for "+ta_requests[0].cid.name+" course.",
			activity_scope="ta"
			)
		session.flash = "TA request accepted successfully"
	redirect(URL("course","main/"+str(ta_requests[0].cid)))
	return locals()

@auth.requires_login()
def reject_ta():
	if auth.user.role != "faculty":
		return "invalid request"
	ta_id =request.args(0)
	ta_requests = db((db.course_ta.id == ta_id)).select()
	if(len(ta_requests) == 0):
		session.flash = "Invalid TA"
	else:
		db((db.course_ta.id == ta_id)).delete()
		db.activity.insert(cid=ta_requests[0].cid, sid=auth.user.id,
			description=auth.user.first_name+" "+auth.user.last_name+" rejected your TAship request for "+ta_requests[0].cid.name+" course.",
			activity_scope="ta"
			)
		session.flash = "TA request rejected successfully"
	redirect(URL("course","main/"+str(ta_requests[0].cid)))
	return locals()

@auth.requires_login()
def home():
	course_id = request.args(0)
	course = db(db.course.id == course_id).select()
	if(course and len(course) == 1):
		course_des = course[0].course_description
		has_edit_access = 0
		faculty = course[0].faculty
		rows = db((db.course_ta.cid==course_id)&(db.course_ta.sid==auth.user.id)&(db.course_ta.approval=='yes')).select()
		if len(rows) == 0:
			is_ta_approved = 0
		else:
			is_ta_approved = 1
			has_edit_access = 1
		if faculty == auth.user.id:
			has_edit_access = 1
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
		session.flash = "File uploaded successfully"
	redirect(URL('course','main/'+str(course_id)))
	return locals()


@auth.requires_login()
def upload_student_assignment():
	data = request.vars
	course_id = request.args(0)
	course = db(db.course.id == course_id).select()
	if(len(course) == 0):
		response.flash = "Invalid course"
	else:
		data = request.vars
		recent_uploads = db((db.course_assignment_upload.aid == data.assignment_id)&(db.course_assignment_upload.sid==auth.user.id)).select()
		if(len(recent_uploads) == 5):
			session.flash = "Maximum upload limit exceeded"
		else:
			db.course_assignment_upload.insert(aid=data.assignment_id,sid=auth.user.id,attachment=data.assignment_file)
			session.flash = "File uploaded successfully"
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
		session.flash = "File uploaded successfully"
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
	else:
		ta_approved = db((db.course_ta.cid == course_id)&(db.course_ta.sid == auth.user.id)&(db.course_ta.approval=='yes')).select()
		if len(ta_approved) == 1 or auth.user.role == "faculty":
			ta_approved = 1
		else:
			ta_approved = 0
		assignments = db((db.course_assignments.deadline >= datetime.datetime.now())&(db.course_assignments.cid == course_id)).select()
		staff_assignments = db((db.course_assignments.cid == course_id)).select()
	return locals()

@auth.requires_login()
def marks():
	course_id = request.args(0)
	course = db(db.course.id == course_id).select()
	if(len(course) == 0):
		response.flash = "Invalid course"
	else:
		course = course.first()
		if (course.faculty == auth.user.id):
			is_staff = 1
		else:
			course = db((db.course_ta.cid == course_id) & (db.course_ta.sid == auth.user.id) &(db.course_ta.approval == 'yes')).select()
			if(len(course) == 1):
				is_staff = 1
			else:
				is_staff = 0
		if is_staff:
			rows = db(db.course_registration.cid == course_id).select()
		else:
			course = db((db.course_registration.cid == course_id)&(db.course_registration.sid == auth.user.id)).select().first()
			if course.mid1 == -1:
				mid1_marks = "TBA"
			else:
				mid1_marks = str(course.mid1) +" / "+ course.cid.mid1_max
			if course.mid2 == -1:
				mid2_marks = "TBA"
			else:
				mid2_marks = str(course.mid2) +" / "+ course.cid.mid2_max
			if course.sem == -1:
				sem_marks = "TBA"
			else:
				sem_marks = str(course.sem) +" / "+ course.cid.sem_max
			assignments = [ i.id for i in db(db.course_assignments.cid == course_id).select()]
			assignments = db((db.course_assignment_upload.aid.belongs(assignments)) & (db.course_assignment_upload.sid == auth.user.id)).select(db.course_assignment_upload.aid,db.course_assignment_upload.id,db.course_assignment_upload.marks,db.course_assignment_upload.sid,db.course_assignment_upload.attachment,db.course_assignment_upload.upload_date.max(),groupby=db.course_assignment_upload.sid)
	return locals()


@auth.requires_login()
def activity():
	course_id = request.args(0)
	course = db(db.course.id == course_id).select()
	if(len(course) == 0):
		response.flash = "Invalid course"
	else:
		activities = db((db.activity.cid==course_id)&(db.activity.activity_scope=='all')).select(orderby=~db.activity.publish_date,limitby=(0, 20))
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
	assignment = db(db.course_assignments.id == assignment_id).select()

	if( len(assignment) == 0):
		session.flash = "Invalid assignment"
	else:
		course_id = assignment.first().cid
		db(db.course_assignments.id == assignment_id).delete()
		db.activity.insert(cid=course_id, sid=auth.user.id,
			description=auth.user.first_name+" "+auth.user.last_name+" deleted assignment, \""+assignment.first().title+"\" for "+assignment.first().cid.name+" course.",
			activity_scope="all"
			)
		session.flash = "Assignment deleted successfully"
		redirect(URL('course','main/'+str(course_id)))

@auth.requires_login()
def delete_resource():
	resource_id = request.args(0)
	resource = db(db.course_resources.id == resource_id).select()
	if( len(resource) == 0):
		sessions.flash = "Invalid resources"
	else:
		course_id = resource.first().cid
		db.activity.insert(cid=course_id, sid=auth.user.id,
			description=auth.user.first_name+" "+auth.user.last_name+" deleted resource, \""+resource.first().title+"\" for "+resource.first().cid.name+" course.",
			activity_scope="all"
			)
		db(db.course_resources.id == resource_id).delete()
		session.flash = "Resource deleted successfully"
		redirect(URL('course','main/'+str(course_id)))

@auth.requires_login()
def view_student_uploads():
	#return str(request.vars)
	assignment_id = request.vars.assignment_upload_id
	rows = db(db.course_assignment_upload.aid==assignment_id).select(db.course_assignment_upload.aid,db.course_assignment_upload.id,db.course_assignment_upload.marks,db.course_assignment_upload.sid,db.course_assignment_upload.attachment,db.course_assignment_upload.upload_date.max(),groupby=db.course_assignment_upload.sid)
	return locals()

@auth.requires_login()
def update_overview():
	course_id = request.args(0)
	content = XML(request.vars.hidediv)
	if db.course(course_id):
		db(db.course.id == course_id).update(course_description=content);
		return "alert('Content updated successfully')";
	else:
		return "alert('error')";

@auth.requires_login()
def update_assignment_marks():
	data = request.vars
	for key in data.keys():
		try:
			data[key] = float(data[key])
		except :
			return "alert('Invalid number')";
		#if type(data[key]) != int and type(data[key]) != float:
	for key in data.keys():
		db(db.course_assignment_upload.id == key).update(marks=data[key]);
	return "alert('Content updated successfully')";

@auth.requires_login()
def update_course_marks():
	data = request.vars
	for key in data.keys():
		try:
			data[key] = float(data[key])
		except :
			return "alert('Invalid number')";
		#if type(data[key]) != int and type(data[key]) != float:
	for key in data.keys():
		arr = key.split("-")
		if arr[0] == "mid1":
			db(db.course_registration.id == arr[1]).update(mid1=data[key]);
		elif arr[0] == "mid2":
			db(db.course_registration.id == arr[1]).update(mid2=data[key]);
		elif arr[0] == "sem":
			db(db.course_registration.id == arr[1]).update(sem=data[key]);
	return "alert('Content updated successfully')";

@auth.requires_login()
def feedback():
	data = request.vars.feedback
	course_id = request.args(0)
	course = db.course(course_id)
	if(course and data):
		to_id = [course.faculty.email]
		to_id.append('adityagaykar@gmail.com') #course.faculty.email
		sub = 'Edify: Feedback from '+auth.user.first_name+' '+auth.user.last_name+' for course '+course.name
		sub += ' [' + request.vars.query + ']'
		mail.send(to=to_id,subject=sub,message=data)
		#mail.send(to=['subash.k3110@gmail.com'],subject='test',message='hello'):
		return "alert('Feeback sent successfully.')";
	else:
		return "alert('Error: invalid args')";

