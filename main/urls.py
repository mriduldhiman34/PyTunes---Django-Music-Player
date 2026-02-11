from django.urls import path
from . import views

urlpatterns = [
    path('', views.hero, name='hero'),
    path('signup/', views.signup, name='signup'),
    path('index/', views.index, name='index'),
    path('user_login/', views.user_login, name='user_login'),
    path('login2_view/', views.login2_view, name='login2_view'),
    path('search/', views.search, name='search'),
    path('get_stream/', views.get_stream, name='get_stream'),
    path('get_lyrics/', views.get_lyrics, name='get_lyrics'),
    path('download_song/', views.download_song, name='download_song'),
    path('contact/', views.contact, name='contact'),
]
