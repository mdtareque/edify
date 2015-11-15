
from gluon.tools import Auth, Service, PluginManager

import time, datetime

auth = Auth(db)
auth.settings.login_next =  URL('home')
auth.settings.register_next = URL('home')

#defining course table

db.define_table('course', 
	Field('name'), 
	Field('faculty','reference auth_user'),
	Field('course_type',requires=IS_IN_SET(('Monsoon','Spring'))),
	Field('course_year','integer',default=time.strftime("%Y")),
	Field('course_description')
	)

db.define_table('course_ta',
	Field('cid','reference course'),
	Field('sid','reference auth_user'),
	Field('approval',requires=IS_IN_SET(('yes','no')),default='no')
	)

db.define_table('course_registration',
	Field('cid','reference course'),
	Field('sid','reference auth_user'),
	Field('mid1','double'),
	Field('mid2','double'),
	Field('sem','float')
	)

db.define_table('course_resources',
	Field('cid','reference course'),
	Field('sid','reference auth_user'),
	Field('title','text',requires=IS_NOT_EMPTY()),
	Field('attachment','upload',requires=IS_NOT_EMPTY()),
	Field('upload_date','datetime',default=datetime.datetime.now())
	)

db.define_table('course_assignments',
	Field('cid','reference course'),
	Field('sid','reference auth_user'),
	Field('total_marks','integer'),
	Field('marks','double'),
	Field('title','text',requires=IS_NOT_EMPTY()),
	Field('attachment','upload',requires=IS_NOT_EMPTY()),
	Field('deadline','datetime',requires=IS_NOT_EMPTY()),
	Field('upload_date','datetime',default=datetime.datetime.now())
	)

db.define_table('activity',
	Field('cid', 'reference course'),
	Field('sid', 'reference auth_user'),
	Field('description', 'text'),
	Field('publish_date','datetime',default=datetime.datetime.now()),	
	Field('activity_scope','text',requires=IS_IN_SET(('faculty','student','ta','all')))
	)


