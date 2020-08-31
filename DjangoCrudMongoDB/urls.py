
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('todo/', include('DjangoCrudApp.urls')),
    path('', include('newTodo.urls'))
]
