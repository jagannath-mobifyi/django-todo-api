import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
# from rest_framework.authentication.models import Token
from rest_framework.test import APITestCase

# from profiles.models import Profile

class TodoApiTestCase(APITestCase):

    # test case for success posting todo
    def test_todo_post(self):
        data = {
            "title": "test_todo",
            "description": "test description"
        }
        response = self.client.post("/task/", data, HTTP_AUTHORIZATION="{'userId':'JDKFLKKSL'}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # posting without authorization key
    def test_todo_post_non_auth(self):
        data = {
            "title": "test_todo",
            "description": "test description"
        }
        response = self.client.post("/task/", data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # posting with wrong auth key
    def test_todo_post_wrong_auth(self):
        data = {
            "title": "test_todo",
            "description": "test description"
        }
        response = self.client.post("/task/", data, HTTP_AUTHORIZATION="")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # posting with missing required payload
    def test_todo_witout_title(self):
        data = {
            "description": "test description"
        }
        response = self.client.post("/task/", data, HTTP_AUTHORIZATION="{'userId':'JDKFLKKSL'}")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def test_todo_get(self):
        response = self.client.get("/task/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(response.data['title'], 'test_todo')

    def test_path_not_found(self):
        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_todo(self):
        response = self.client.delete("/task/")

    