# music/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from rest_framework import generics, filters
from rest_framework.pagination import PageNumberPagination
from .models import Artist, Album, Track, Comment, Genre
from .serializers import ArtistSerializer, AlbumSerializer, TrackSerializer, CommentSerializer
from .forms import TrackUploadForm

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# === API Views ===

class ArtistList(generics.ListCreateAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    pagination_class = StandardResultsSetPagination

class ArtistDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer

class AlbumList(generics.ListCreateAPIView):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    pagination_class = StandardResultsSetPagination

class AlbumDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer

class TrackList(generics.ListCreateAPIView):
    serializer_class = TrackSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'genres__name', 'artists__name', 'album__title']

    def get_queryset(self):
        queryset = Track.objects.all().select_related('album').prefetch_related('artists', 'genres')
        title = self.request.query_params.get('title')
        genre = self.request.query_params.get('genre')
        artist = self.request.query_params.get('artist')
        album = self.request.query_params.get('album')
        search = self.request.query_params.get('search')

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(genres__name__icontains=search) |
                Q(artists__name__icontains=search) |
                Q(album__title__icontains=search)
            ).distinct()
        else:
            if title:
                queryset = queryset.filter(title__icontains=title)
            if genre:
                queryset = queryset.filter(genres__code=genre)
            if artist:
                queryset = queryset.filter(artists__name__icontains=artist)
            if album:
                queryset = queryset.filter(album__title__icontains=album)

        return queryset.distinct()

class TrackDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Track.objects.all().select_related('album').prefetch_related('artists', 'genres')
    serializer_class = TrackSerializer

class CommentList(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        track_id = self.request.query_params.get('track')
        if track_id:
            return Comment.objects.filter(track_id=track_id)
        return Comment.objects.all()

class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

def autocomplete_artists(request):
    query = request.GET.get('q', '').strip()
    if query:
        artists = Artist.objects.filter(name__icontains=query).order_by('name')[:10]
        data = [{'id': a.id, 'name': a.name} for a in artists]
    else:
        data = []
    return JsonResponse(data, safe=False)

def autocomplete_albums(request):
    query = request.GET.get('q', '').strip()
    if query:
        albums = Album.objects.filter(title__icontains=query).order_by('title')[:10]
        data = [{'id': a.id, 'title': a.title} for a in albums]
    else:
        data = []
    return JsonResponse(data, safe=False)

def home_page(request):
    search_query = request.GET.get('search', '')
    genre_filter = request.GET.get('genre', '')
    artist_filter = request.GET.get('artist', '')

    tracks = Track.objects.all().select_related('album').prefetch_related('artists', 'genres')

    if search_query:
        tracks = tracks.filter(
            Q(title__icontains=search_query) |
            Q(genres__name__icontains=search_query) |
            Q(artists__name__icontains=search_query) |
            Q(album__title__icontains=search_query)
        ).distinct()
    if genre_filter:
        tracks = tracks.filter(genres__code=genre_filter)
    if artist_filter:
        tracks = tracks.filter(artists__name__icontains=artist_filter)

    tracks = tracks.order_by('-uploaded_at')

    paginator = Paginator(tracks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    all_genres = Genre.objects.all()
    all_artists = Artist.objects.all()

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'genre_filter': genre_filter,
        'artist_filter': artist_filter,
        'all_genres': all_genres,
        'all_artists': all_artists,
    }
    return render(request, 'home.html', context)

def upload_page(request):
    if request.method == 'POST':
        form = TrackUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Трек успешно загружен!')
            return redirect('home')
    else:
        form = TrackUploadForm()

    # Передаём список жанров в шаблон для JS
    genres = Genre.objects.all()
    return render(request, 'upload.html', {'form': form, 'genres': genres})