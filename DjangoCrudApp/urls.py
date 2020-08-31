from django.urls import path

from .views import add_task, findAll, update, delete

urlpatterns = [
    path('add/', add_task, name="add_task"),
    path('', findAll, name="get_all_task"),
    path('update/', update, name="update_task"),
    path('delete/', delete, name="delete_task"),
]
