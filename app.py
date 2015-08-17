#!flask/bin/python

"""Alternative version of the ToDo RESTful server implemented using the
Flask-RESTful extension."""

from bson.objectid import ObjectId
from pymongo import MongoClient

from flask import Flask, jsonify, abort, make_response, request
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth

import secrets
import models
import helpers
import sm2

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

class CourseListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location='json')
        super(CourseListAPI, self).__init__()

    def get(self):
        return helpers.getItems(handle, "courses", models.course_fields)

    def post(self):
        args = self.reqparse.parse_args()
        return helpers.postItem(handle, "courses", models.course_fields, args), 201


class UserListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('answeredQuestions', type=list, required=True, default=[], location='json')
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
        return helpers.getItems(handle, "questions", models.question_fields, courseId)

    def post(self, courseId):
        args = self.reqparse.parse_args()
        return helpers.postItem(handle, "questions", models.question_fields, args, courseId), 201

class CourseAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location='json')
        super(CourseAPI, self).__init__()

    def get(self, _id):
        return helpers.getItem(handle, "courses", models.course_fields, _id)

    def put(self, _id):
        args = self.reqparse.parse_args()
        return helpers.putItem(handle, "courses", models.course_fields, args, _id)

    def delete(self, _id):
        return helpers.deleteItem(handle, "courses", _id)

class UserAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('answeredQuestions', type=list, default=[], location='json')
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
        self.reqparse.add_argument('courseId', type=str, location='json')
        super(QuestionAPI, self).__init__()

    def get(self, courseId, _id):
        return helpers.getItem(handle, "questions", models.question_fields, _id, courseId)

    def put(self, courseId, _id):
        args = self.reqparse.parse_args()
        return helpers.putItem(handle, "questions", models.question_fields, args, _id, courseId)

    def delete(self, courseId, _id):
        return helpers.deleteItem(handle, "questions", _id, courseId)

api.add_resource(CourseListAPI, '/api/courses', endpoint='courses')
api.add_resource(CourseAPI, '/api/courses/<_id>', endpoint='course')
api.add_resource(QuestionListAPI, '/api/courses/<courseId>/questions', endpoint='questions')
api.add_resource(QuestionAPI, '/api/courses/<courseId>/questions/<_id>', endpoint='question')
api.add_resource(UserListAPI, '/api/users', endpoint='users')
api.add_resource(UserAPI, '/api/users/<_id>', endpoint='user')

@app.route('/')
def getIndex():
    return 'Welcome to Askii'

@app.route('/developers')
def getDevelopers():
    return 'Welcome to the Askii Dev Docs. This is where the API explanation will live.'

@app.route('/api')
@auth.login_required
def getApi():
    return 'Welcome to the Askii API'

@app.route('/api/courses/<courseId>/answer-question', methods=['POST'])
@auth.login_required
def answerQuestion(courseId):

    if 'userId' and 'questionId' not in request.args:
        abort(404)

    userId = request.args['userId']
    questionId = request.args['questionId']
    if len(userId) != helpers.OBJECT_ID_LENGTH or len(questionId) != helpers.OBJECT_ID_LENGTH: 
        abort(404)

    question = handle.questions.find_one(ObjectId(questionId))
    if len(question) == 0 or question['courseId'] != courseId: 
        abort(404)
    
    user = handle.users.find_one(ObjectId(userId))
    if not user:
        abort(404)

    ct = 0
    to_update = {}
    to_update_index = None
    for answered_question in user['answeredQuestions']:
        if answered_question['courseId']==courseId and answered_question['questionId']==questionId:
            to_update = answered_question
            to_update_index = ct
        ct += 1

    quality = 5
    updated_fields = {}
    updated_fields['e-factor'] = sm2.getEFactor(to_update, quality)
    updated_fields['i-interval'] = sm2.getIInterval(to_update, quality)
    updated_fields['reply_at']=sm2.getReplyAt(to_update, quality)
    
    if to_update_index != None:
        updated_fields["courseId"]=to_update["courseId"]
        updated_fields["questionId"]=to_update["questionId"]
        user['answeredQuestions'][to_update_index]=updated_fields
    else:
        updated_fields["courseId"]=courseId
        updated_fields["questionId"]=questionId
        user['answeredQuestions'].append(updated_fields)

    handle.users.update({"_id": ObjectId(userId)}, {'$set': {'answeredQuestions': user['answeredQuestions']}})
    return 'Updated question %s for user %s' % (questionId, user["_id"])


if __name__ == '__main__':
    app.run(debug=True)

