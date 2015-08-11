#!flask/bin/python

"""Alternative version of the ToDo RESTful server implemented using the
Flask-RESTful extension."""

from bson.objectid import ObjectId

from flask import Flask, jsonify, abort, make_response
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth

import secrets

app = Flask(__name__, static_url_path="")
api = Api(app)
auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    if username == secrets.username:
        return secrets.password
    return None


@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)

questions = [
    {
        'id':  ObjectId(),
        'prompt': u'Buy groceries',
        'answer': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'hint': u'Hinting',
        'done': False,
        'courseId': u'test',
        'initialOrdering': 0.0
    },
    {
        'id':  ObjectId(),
        'prompt': u'Learn Python',
        'answer': u'Need to find a good Python tutorial on the web',
        'hint': u'Hinting',
        'done': False,
        'courseId': u'test',
        'initialOrdering': 1.0
    }
]

users = [
    {
        'id': ObjectId(),
        'personalData': {
            "email": "test@test.com"
        },
        'answeredQuestions': {}
    }
]

question_fields = {
    'prompt': fields.String,
    'answer': fields.String,
    'hint': fields.String,
    'done': fields.Boolean,
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
    'answeredQuestions': fields.Nested(answered_questions_fields)
}


class UserListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('answeredQuestions', type=dict, required=True, default={}, location='json')
        self.reqparse.add_argument('personalData', type=dict, required=True, default={}, location='json')
        super(UserListAPI, self).__init__()

    def get(self):
        return {'users': [marshal(user, user_fields) for user in users]}

    def post(self):
        args = self.reqparse.parse_args()
        user = {
            'id': ObjectId(),
            'personalData': args['personalData'],
            'answeredQuestions': args['answeredQuestions']
        }
        users.appends(user)
        return {'users': marshal(user, user_fields)}, 201


class QuestionListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('prompt', type=str, required=True, help='No question prompt provided', location='json')
        self.reqparse.add_argument('answer', type=str, default="", location='json')
        self.reqparse.add_argument('hint', type=str, default="", location='json')
        self.reqparse.add_argument('initialOrdering', type=float, default=0.0, location='json')
        self.reqparse.add_argument('courseId', type=str, default="", location='json')
        super(QuestionListAPI, self).__init__()

    def get(self, courseId):
        return {'questions': [marshal(question, question_fields) for question in questions]}

    def post(self, courseId):
        args = self.reqparse.parse_args()
        question = {
            'id':  ObjectId(),
            'prompt': args['prompt'],
            'answer': args['answer'],
            'hint': args['hint'],
            'courseId': args['courseId'],
            'initialOrdering': args['initialOrdering'],
            'done': False
        }
        questions.append(question)
        return {'questions': marshal(question, question_fields)}, 201


class UserAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('answeredQuestions', type=dict, required=True, default={}, location='json')
        self.reqparse.add_argument('personalData', type=dict, default={}, location='json')
        super(UserAPI, self).__init__()

    def get(self, id):
        id = ObjectId(id)
        user = [user for user in users if user['id'] == id]
        if len(user) == 0:
            abort(404)
        return {'user': marshal(user[0], user_fields)}

    def put(self, id):
        id = ObjectId(id)
        user = [user for user in users if user['id'] == id]
        if len(user) == 0:
            abort(404)
        user = user[0]
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                user[k] = v
        return {'user': marshal(user, user_fields)}

    def delete(self, id):
        id = ObjectId(id)
        user = [user for user in users if user['id'] == id]
        if len(user) == 0:
            abort(404)
        users.remove(user[0])
        return {'result': True}

class QuestionAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('prompt', type=str, location='json')
        self.reqparse.add_argument('answer', type=str, location='json')
        self.reqparse.add_argument('hint', type=str, location='json')
        self.reqparse.add_argument('initialOrdering', type=float, location='json')
        self.reqparse.add_argument('done', type=bool, location='json')
        super(QuestionAPI, self).__init__()

    def get(self, courseId, id):
        id = ObjectId(id)
        question = [question for question in questions if question['id'] == id]
        if len(question) == 0:
            abort(404)
        return {'question': marshal(question[0], question_fields)}

    def put(self, courseId, id):
        id = ObjectId(id)
        question = [question for question in questions if question['id'] == id]
        if len(question) == 0:
            abort(404)
        question = question[0]
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                question[k] = v
        return {'question': marshal(question, question_fields)}

    def delete(self, courseId, id):
        id = ObjectId(id)
        question = [question for question in questions if question['id'] == id]
        if len(question) == 0:
            abort(404)
        questions.remove(question[0])
        return {'result': True}

api.add_resource(QuestionListAPI, '/api/courses/<courseId>/questions', endpoint='questions')
api.add_resource(QuestionAPI, '/api/courses/<courseId>/questions/<id>', endpoint='question')
api.add_resource(UserListAPI, '/api/users', endpoint='users')
api.add_resource(UserAPI, '/api/users/<id>', endpoint='user')


if __name__ == '__main__':
    app.run(debug=True)