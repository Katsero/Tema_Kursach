# music/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # HTML-страницы
    path('', views.home_page, name='home'),
    path('upload/', views.upload_page, name='upload'),

    # Autocomplete API
    path('api/artists/search/', views.autocomplete_artists, name='autocomplete-artists'),
    path('api/albums/search/', views.autocomplete_albums, name='autocomplete-albums'),

    # Основные API
    path('api/artists/', views.ArtistList.as_view(), name='artist-list'),
    path('api/artists/<int:pk>/', views.ArtistDetail.as_view(), name='artist-detail'),
    path('api/albums/', views.AlbumList.as_view(), name='album-list'),
    path('api/albums/<int:pk>/', views.AlbumDetail.as_view(), name='album-detail'),
    path('api/tracks/', views.TrackList.as_view(), name='track-list'),
    path('api/tracks/<int:pk>/', views.TrackDetail.as_view(), name='track-detail'),
    path('api/comments/', views.CommentList.as_view(), name='comment-list'),
    path('api/comments/<int:pk>/', views.CommentDetail.as_view(), name='comment-detail'),
]