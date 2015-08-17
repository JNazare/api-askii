from flask.ext.restful import fields

# Questions
question_fields = {
    'prompt': fields.String,
    'answer': fields.String,
    'hint': fields.String,
    'courseId': fields.String,
    'initialOrdering': fields.Float,
    'uri': fields.Url('question')
}


# Users
personal_data_fields = {}
personal_data_fields['email']=fields.String
personal_data_fields['name']=fields.String

answer_fields = {}
answer_fields['e-factor']=fields.Float
answer_fields['i-interval']=fields.Float
answer_fields['reply_at']=fields.String
answer_fields['courseId']=fields.String
answer_fields['questionId']=fields.String

user_fields = {
    'personalData': fields.Nested(personal_data_fields),
    'answeredQuestions': fields.List(fields.Nested(answer_fields)),
    'uri': fields.Url('user')
}


# Courses
course_fields = {
	'name': fields.String,
	'uri': fields.Url('course')
}