from bson.objectid import ObjectId
from flask.ext.restful import marshal
from flask import abort
import models

def getItems(handle, collection, item_fields):
    items = handle[collection].find()
    return {collection: [marshal(item, item_fields) for item in items]}

def getItem(handle, collection, item_fields, _id):
    _id = ObjectId(_id)
    item = handle[collection].find_one(_id)
    print item
    if len(item) == 0:
        abort(404)
    return {collection: marshal(item, item_fields)}

def postItem(handle, collection, item_fields, args):
    item = {}
    for k in args.keys():
        item[k] = args[k]
    handle[collection].insert(item)
    return {collection: marshal(item, item_fields)}

def putItem(handle, collection, item_fields, args, _id):
    _id = ObjectId(_id)
    item = handle[collection].find_one(_id)
    if len(item) == 0:
        abort(404)
    for k, v in args.items():
        if v is not None:
            if type(v) is dict:
                for skey in v.keys():
                    sval = v[skey]
                    handle[collection].update({"_id": ObjectId(unicode(item['_id']))}, {'$set': {k+"."+skey: sval}})
            else:
                handle[collection].update({"_id": ObjectId(unicode(item['_id']))}, {'$set': {k: v}})
    item = handle[collection].find_one(_id)
    return {collection: marshal(item, item_fields)}

def deleteItem(handle, collection, _id):
    _id = ObjectId(_id)
    item = handle[collection].find_one(_id)
    if len(item) == 0:
        abort(404)
    handle[collection].remove({"_id": ObjectId(unicode(item["_id"]))})
    return {'result': True}