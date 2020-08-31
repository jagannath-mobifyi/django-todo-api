from django.shortcuts import render
from rest_framework.views import APIView
from drf_yasg.utils import no_body, swagger_auto_schema
from drf_yasg import openapi
import sys
from django.http import JsonResponse
from rest_framework.decorators import action
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

# Create your views here.
client = MongoClient('localhost', 27017)
db = client["pymongoTodo"]
collection = db["pymongoTodo"]


class Tasks(APIView):
    @swagger_auto_schema(method='get', tags=['Tasks'],
        operation_description="API to get all todo tasks",
        operation_summary="API to get all Tasks",
        required=['AUTHORIZATION','language'],
        manual_parameters=[
            openapi.Parameter(
                name= 'language', in_=openapi.IN_HEADER, 
                type=openapi.TYPE_STRING, 
                required=True,
                description="Language, Ex-en/hi/sp/bn...",
                default="en"
            ),
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description='authorization token',
                default="{'userId':'5ee338bd22b40d25c825e696','userType':'user','metaData':''}",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                name='status',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="status 1-Active, 2-Deleted",
                default=1
            ),
            openapi.Parameter(
                name = 'limit',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="limit",
                default=20
            ),
            openapi.Parameter(
                name = 'skip',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="skip documents",
                default=0
            ),
            openapi.Parameter(
                name = 'searchText',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="search by title."
            ),
            openapi.Parameter(
                name = 'id',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="get todo by todo id",
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'result': openapi.Schema(
                        type=openapi.TYPE_ARRAY, 
                        items=openapi.Items(
                            type=openapi.TYPE_STRING
                        )
                    ),
                    'message': openapi.Schema(type=openapi.TYPE_STRING,
                        description="message for the success",
                        example="Task list Found SuccesFully"
                        ),
                    'totalCount': openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description="total number of data",
                        example=1
                        ),
                }),
            401: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="token not found / token expired",
                        example="unauthorized!"
                    )
                }
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Invalid request data",
                        example="Bad request!"
                    )
                }
            ),
            500: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="server error",
                        example="Internal server error!"
                    )
                }
            )
        }
    )
    @action(detail=False, methods=['get'])
    def get(self, request):
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


    @swagger_auto_schema(method='post', tags=['Tasks'],
        operation_summary='Post a new todo',
        operation_description='API to post new todo',
        required=['AUTHORIZATION','language'],
        manual_parameters=[
            openapi.Parameter(
                name='language',
                in_=openapi.IN_HEADER,
                description='Language',
                default='en',
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description='authorization token',
                default="{'userId':'5ee338bd22b40d25c825e696','userType':'user','metaData':''}",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['title'],
            properties={
                'title': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    default="",
                    description='title of todo',
                ),
                'description': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    default="",
                    description='description of todo',
                )
            }
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type= openapi.TYPE_STRING,
                        description="response message of the request",
                        example="Task Added Successfylly....!!!!"
                    )
                }
            ),
            401: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="token not found / token expired",
                        example="unauthorized!"
                    )
                }
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Invalid request data",
                        example="Bad request!"
                    )
                }
            ),
            404: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="page not found",
                        example="page not found!"
                    )
                }
            ),
            500: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="server error",
                        example="Internal server error!"
                    )
                }
            )
        }
    )
    @action(detail=False, methods=['post'])
    def post(self, request):
        try:
            token = request.META['HTTP_AUTHORIZATION']
            if token == "":
                response_data = {
                    "message": "Unauthorized!"
                }
                return JsonResponse(response_data, safe=False, status=401)
            else:
                req = request.data 
                payload = {
                    "title": req['title'],
                    "description": req['description'] or "",
                    "status": 1,
                    "createdAt": datetime.timestamp(datetime.now()) * 1000,
                    "updatedAt": datetime.timestamp(datetime.now()) * 1000
                }
                # checking for duplicate entry 
                duplicate_task = collection.find_one({"status":1, "title": req['title']})
                if(duplicate_task):
                    result = {
                        "message": "Duplicate Entry!"
                    }
                    return JsonResponse(result, safe=False, status=209)

                # inserting payload into db
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


    @swagger_auto_schema(method='patch', tags=['Tasks'],
        operation_summary='Update a new todo',
        operation_description='API to update new todo',
        required=['AUTHORIZATION','language'],
        manual_parameters=[
            openapi.Parameter(
                name='language',
                in_=openapi.IN_HEADER,
                description='Language',
                default='en',
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description='authorization token',
                default="{'userId':'5ee338bd22b40d25c825e696','userType':'user','metaData':''}",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id'],
            properties={
                'id': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='id of the todo to update',
                ),
                'title': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='title of todo',
                ),
                'description': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='description of todo',
                )
            }
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type= openapi.TYPE_STRING,
                        description="response message of the request",
                        example="Task Updated Successfylly....!!!!"
                    )
                }
            ),
            401: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="token not found / token expired",
                        example="unauthorized!"
                    )
                }
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Invalid request data",
                        example="Bad request!"
                    )
                }
            ),
            404: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="page not found",
                        example="page not found!"
                    )
                }
            ),
            500: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="server error",
                        example="Internal server error!"
                    )
                }
            )
        }
    )
    @action(detail=False, methods=['patch'])
    def patch(self, request):
        try:
            token = request.META['HTTP_AUTHORIZATION']
            if token == "":
                response_data = {
                    "message": "Unauthorized!"
                }
                return JsonResponse(response_data, safe=False, status=401)
            else:
                req = request.data
                condition = {'_id': ObjectId(req.get('id'))}
                payload = {}
                if req.get('title'):
                    payload['title'] = req.get('title')
                if req.get('description'):
                    payload['description'] = req.get('description')
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


    @swagger_auto_schema(method='put', tags=['Tasks'],
        operation_summary='Delete a  todo',
        operation_description='API to delete  todo',
        required=['AUTHORIZATION','language'],
        manual_parameters=[
            openapi.Parameter(
                name='language',
                in_=openapi.IN_HEADER,
                description='Language',
                default='en',
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description='authorization token',
                default="{'userId':'5ee338bd22b40d25c825e696','userType':'user','metaData':''}",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'status'],
            properties={
                'id': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Todo Id",
                    example="5f4cc49286e20a0c8b8582aa"
                ),
                'status': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description='Action type Ex- 1-activate / 2-delete',
                    default=2
                )
            }
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type= openapi.TYPE_STRING,
                        description="response message of the request",
                        example="Task deleted/updated Successfylly....!!!!"
                    )
                }
            ),
            401: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="token not found / token expired",
                        example="unauthorized!"
                    )
                }
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Invalid request data",
                        example="Bad request!"
                    )
                }
            ),
            404: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="page not found",
                        example="page not found!"
                    )
                }
            ),
            500: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="server error",
                        example="Internal server error!"
                    )
                }
            )
        }
    )
    @action(detail=False, methods=['put'])
    def put(self, request):
        try:
            token = request.META['HTTP_AUTHORIZATION']
            if token == "":
                response_data = {
                    "message": "Unauthorized!"
                }
                return JsonResponse(response_data, safe=False, status=401)
            else:
                req = request.data
                condition = {'_id': ObjectId(req.get('id'))}
                action = {'$set': {'status': req.get('status') } }
                data = collection.find(condition)
                data = list(data)
                if len(data):
                    collection.update_one(condition, action)
                    result = {
                        "message": "Todo deleted/updated successfully!"
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

    @swagger_auto_schema(
        method='delete', 
        tags=['Tasks'],
        operation_summary='Permanently delete a todo',
        operation_description='API to permanently delete a todo',
        required=['AUTHORIZATION','language'],
        manual_parameters=[
            openapi.Parameter(
                name='language',
                in_=openapi.IN_HEADER,
                description='Language',
                default='en',
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description='authorization token',
                default="{'userId':'5ee338bd22b40d25c825e696','userType':'user','metaData':''}",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id'],
            properties={
                'id': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Todo Id",
                    example="5f4cc49286e20a0c8b8582aa"
                )
            }
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type= openapi.TYPE_STRING,
                        description="response message of the request",
                        example="Task has been permanently deleted Successfylly....!!!!"
                    )
                }
            ),
            401: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="token not found / token expired",
                        example="unauthorized!"
                    )
                }
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Invalid request data",
                        example="Bad request!"
                    )
                }
            ),
            404: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="page not found",
                        example="page not found!"
                    )
                }
            ),
            500: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="server error",
                        example="Internal server error!"
                    )
                }
            )
        }
    )
    @action(detail=False, methods=['delete'])
    def delete(self, request):
        try:
            token = request.META['HTTP_AUTHORIZATION']
            if token == "":
                response_data = {
                    "message": "Unauthorized!"
                }
                return JsonResponse(response_data, safe=False, status=401)
            else:
                req = request.data
                condition = {'_id': ObjectId(req.get('id'))}
                data = collection.find(condition)
                data = list(data)
                if len(data):
                    collection.delete_one(condition)
                    result = {
                        "message": "Todo has been permanently deleted successfully!"
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


