from django.contrib import admin
from django.urls import path
from home import views

admin.site.site_header = "DataTalk Admin"
admin.site.site_title = "DataTalk Admin Portal"
admin.site.index_title = "Welcome to DataTalk Admin Portal"

urlpatterns = [
    path('', views.index , name='home'),
    path('choose', views.choose , name='.choose'),
    path('aviation', views.aviation , name='aviation'),
    path('choose', views.choose , name='choose'),
    path('banking', views.banking , name='banking'),
    path('ecommerse', views.ecommerse , name='ecommerse'),
    path('sqlconnector', views.sqlconnector , name='sqlconnector'),
    path("connect-to-database/", views.connect_to_database, name="connect_to_database"),
    
    path('home', views.home , name='home'),
    path('chat', views.chat_view , name='chat'),
]