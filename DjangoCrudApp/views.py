import pymongo
import dns
from django.http import HttpResponse, JsonResponse
from pymongo import MongoClient
from bson.objectid import ObjectId
from django.views.decorators.csrf import csrf_exempt
# from DjangoCrudApp.models import Posts
import json
from datetime import datetime
# cluster = MongoClient("mongodb+srv://jagan:jagan%40jagan@cluster0-9u9ce.mongodb.net/test?retryWrites=true&w=majority")

client = MongoClient('localhost', 27017)
db = client["pymongoTodo"]
collection = db["pymongoTodo"]

# def serialize(a):
#     a['_id'] = str(ind['_id']
#     return;

@csrf_exempt
def add_task(request):
    if request.method == 'POST':
        try:
            req = json.loads(request.body)
            payload = {
                "title": req['title'],
                "description": req['description'] or "",
                "status": req['status'],
                "createdAt": datetime.timestamp(datetime.now()) * 1000,
                "updatedAt": datetime.timestamp(datetime.now()) * 1000
            }
            collection.insert_one(payload)
            result = {
                "message": "Data inserted successfully!"
            }
            return JsonResponse(result, safe=False, status=201)

        except Exception as ex:
            print('\n\n.............',ex,'\n\n')
            result = {
                "message": "Internal server error!"
            }
            return JsonResponse(result, safe=False, status=500)
    else:
        result = { "message": "Method not allowed!" }
        return JsonResponse(result, safe=False, status=400)


@csrf_exempt
def findAll(request):
    if request.method == 'GET':
        try:
            condition = {}
            limit = int(request.GET.get('limit') or 20)
            skip = int(request.GET.get('skip') or 0)
            sort = [("updatedAt", -1)]
            if request.GET.get('status'):
                condition['status'] = int(request.GET.get('status') or 1)
            if request.GET.get('searchText'):
                condition['title'] = {'$regex': request.GET.get('searchText')}
            if request.GET.get('id'):
                condition['_id'] = ObjectId(request.GET.get('id'))
            if request.GET.get('fromDate') and request.GET.get('toDate'):
                condition['updatedAt'] = { '$gte': request.GET.get('fromDate'), '$lte': request.GET.get('fromDattoDatee') }

            # # db query- getting data from db
            dbRes = collection.find(condition).sort(sort).limit(limit).skip(skip)
            totalCount = collection.find(condition).count()
            response = []

            for data in dbRes:
                response.append({
                    '_id': str(data['_id']),
                    'title': data['title'],
                    'description': data['description'] or "",
                    'status': data['status'],
                    'createdAt': data['createdAt'],
                    'updatedAt': data['updatedAt']
                })
            if not len(response):
                result = {
                    "message": "no data found",
                    "data": []
                }
                return JsonResponse(result, safe=False, status=204)
            else:
                result = {
                    "message": "success",
                    "data": response,
                    "totalCount": totalCount
                }
                return JsonResponse(result, safe=False, status=200)

        except Exception as ex:
            print('\n\n.............',ex,'\n\n')
            result = {
                "message": "Internal server error!"
            }
            return JsonResponse(result, safe=False, status=500)
    else:
        result = { "message": "Method not allowed!" }
        return JsonResponse(result, safe=False, status=400)
    
@csrf_exempt
def update(request):
    if request.method == 'PATCH':
        try:
            req = json.loads(request.body)
            condition = {'_id': ObjectId(req.get('id'))}
            payload = {}
            if req.get('title'):
                payload['title'] = req.get('title')
            if req.get('description'):
                payload['description'] = req.get('description')
            if req.get('status'):
                payload['status'] = int(req.get('status'))
            if not len(payload.keys()):
                result = {
                    "message": "Bad request!"
                }
                return JsonResponse(result, safe=False, status=400)
            payload['updatedAt'] = datetime.timestamp(datetime.now()) * 1000
            data = collection.find(condition)
            data = list(data)
            if len(data):
                action = {'$set': payload}
                collection.update_one(condition, action)

                result = {
                    "message": "Todo Updated successfully!"
                }
                return JsonResponse(result, safe=False, status=201)
            else:
                result = {
                    "message": "Data not found"
                }
                return JsonResponse(result, safe=False, status=204)

        except Exception as ex:
            print('\n\n.............',ex,'\n\n')
            result = {
                "message": "Internal server error!"
            }
            return JsonResponse(result, safe=False, status=500)
    else:
        result = { "message": "Method not allowed!" }
        return JsonResponse(result, safe=False, status=400)

@csrf_exempt
def delete(request):
    if request.method == 'DELETE':
        req = json.loads(request.body)
        condition = {'_id': ObjectId(req.get('id'))}
        try:
            data = collection.find(condition)
            data = list(data)
            if len(data):
                collection.delete_one(condition)
                result = {
                    "message": "Todo deleted successfully!"
                }
                return JsonResponse(result, safe=False, status=201)
            else:
                result = {
                    "message": "Data not found"
                }
                return JsonResponse(result, safe=False, status=204)

        except Exception as ex:
            print('\n\n.............',ex,'\n\n')
            result = {
                "message": "Internal server error!"
            }
            return JsonResponse(result, safe=False, status=500)
    else:
        result = { "message": "Method not allowed!" }
        return JsonResponse(result, safe=False, status=400)
































# from django.http import HttpResponse

# # Create your views here.
# from DjangoCrudApp.models import Posts

# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# def add_task(request):
#     comment=request.POST.get("comment").split(",")
#     tags=request.POST.get("tags").split(",")
#     user_details={"first_name":request.POST.get('first_name'),"last_name":request.POST.get('last_name')}

#     post = Posts(post_title=request.POST.get('post_title'), post_description=request.POST.get('post_description'), comment=comment, tags=tags, user_details=user_details)
#     post.save()
#     return HttpResponse('Inserted')

# def get_all(request):
#     pass

# def get_by_id(request, id):
#     post = Posts.objects.get(_id=ObjectId(id))
#     print(post)
#     return HttpResponse(post)

# def update(request, id):
#     pass

# def delete(request, id):
#     pass