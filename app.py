#!flask/bin/python

"""Alternative version of the ToDo RESTful server implemented using the
Flask-RESTful extension."""

from bson.objectid import ObjectId
from pymongo import MongoClient

from flask import Flask, jsonify, abort, make_response
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth

import secrets
import models
import helpers

# add courseId field automatically based on route

### MONGO CONNECTION ###
def connect():
    mongo_keys = secrets.MONGO_KEYS
    connection = MongoClient(mongo_keys[0],mongo_keys[1])
    handle = connection[mongo_keys[2]]
    handle.authenticate(mongo_keys[3],mongo_keys[4])
    return handle

app = Flask(__name__, static_url_path="")
api = Api(app)
auth = HTTPBasicAuth()
handle = connect()


@auth.get_password
def get_password(username):
    if username == secrets.username:
        return secrets.password
    return None


@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)


class UserListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('answeredQuestions', type=dict, required=True, default={}, location='json')
        self.reqparse.add_argument('personalData', type=dict, required=True, default={}, location='json')
        super(UserListAPI, self).__init__()

    def get(self):
        return helpers.getItems(handle, "users", models.user_fields)

    def post(self):
        args = self.reqparse.parse_args()
        return helpers.postItem(handle, "users", models.user_fields, args), 201


class QuestionListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        questions = handle.questions.find()
        questions = [question for question in questions]
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('prompt', type=str, required=True, help='No question prompt provided', location='json')
        self.reqparse.add_argument('answer', type=str, default="", location='json')
        self.reqparse.add_argument('hint', type=str, default="", location='json')
        self.reqparse.add_argument('initialOrdering', type=float, default=float(len(questions)), location='json')
        self.reqparse.add_argument('courseId', type=str, default="", location='json')
        super(QuestionListAPI, self).__init__()

    def get(self, courseId):
        return helpers.getItems(handle, "questions", models.question_fields)

    def post(self, courseId):
        args = self.reqparse.parse_args()
        return helpers.postItem(handle, "questions", models.question_fields, args), 201

class UserAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('answeredQuestions', type=dict, default={}, location='json')
        self.reqparse.add_argument('personalData', type=dict, default={}, location='json')
        super(UserAPI, self).__init__()

    def get(self, _id):
        return helpers.getItem(handle, "users", models.user_fields, _id)

    def put(self, _id):
        args = self.reqparse.parse_args()
        return helpers.putItem(handle, "users", models.user_fields, args, _id)

    def delete(self, _id):
        return helpers.deleteItem(handle, "users", _id)

class QuestionAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('prompt', type=str, location='json')
        self.reqparse.add_argument('answer', type=str, location='json')
        self.reqparse.add_argument('hint', type=str, location='json')
        self.reqparse.add_argument('initialOrdering', type=float, location='json')
        super(QuestionAPI, self).__init__()

    def get(self, courseId, _id):
        return helpers.getItem(handle, "questions", models.question_fields, _id)

    def put(self, courseId, _id):
        args = self.reqparse.parse_args()
        return helpers.putItem(handle, "questions", models.question_fields, args, _id)

    def delete(self, courseId, _id):
        return helpers.deleteItem(handle, "questions", _id)

api.add_resource(QuestionListAPI, '/api/courses/<courseId>/questions', endpoint='questions')
api.add_resource(QuestionAPI, '/api/courses/<courseId>/questions/<_id>', endpoint='question')
api.add_resource(UserListAPI, '/api/users', endpoint='users')
api.add_resource(UserAPI, '/api/users/<_id>', endpoint='user')


if __name__ == '__main__':
    app.run(debug=True)