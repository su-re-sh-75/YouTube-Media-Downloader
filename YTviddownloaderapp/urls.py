from django.urls import path
from . import views
# URL patterns for all features connected with respective views(functions)
app_name = "ytproject"
urlpatterns = [
    path('', views.home, name="home"),
    path('download/', views.video_list, name="vid_list"),
    path('download/<resolution>', views.video_download, name = "video_download"),
    path('audio/', views.audio_home, name="audio_home"),
    path('audio/auddownload/', views.audio_list, name="audio_list"),
    path('audio/auddownload/<abr>', views.audio_download, name="audio_download"),
    path('playlist/', views.playlist_home, name='playlist_home'),
    path('playlist/pldownload/', views.playlist_download, name='playlist_download'),
    path('search/', views.search, name='search'),
    path('history/', views.view_history, name='view_history')
]
