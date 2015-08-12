from flask.ext.restful import fields

question_fields = {
    'prompt': fields.String,
    'answer': fields.String,
    'hint': fields.String,
    'courseId': fields.String,
    'initialOrdering': fields.Float,
    'uri': fields.Url('question')
}

personal_data_fields = {}
personal_data_fields['email']=fields.String
personal_data_fields['name']=fields.String

answered_questions_fields = {}

user_fields = {
    'personalData': fields.Nested(personal_data_fields),
    'answeredQuestions': fields.Nested(answered_questions_fields),
    'uri': fields.Url('user')
}