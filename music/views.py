# music/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django import forms
from rest_framework import generics, filters
from rest_framework.pagination import PageNumberPagination
from .models import CustomUser, Artist, Album, Track, Comment, Genre
from .serializers import ArtistSerializer, AlbumSerializer, TrackSerializer, CommentSerializer
from .forms import TrackUploadForm

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

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
        return Track.objects.filter(status=Track.STATUS_APPROVED).select_related('album').prefetch_related('artists', 'genres')

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

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = CustomUser
        fields = ("email", "password1", "password2")
        labels = {
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect('home')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Неверный email или пароль.")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def home_page(request):
    search_query = request.GET.get('search', '')
    genre_filter = request.GET.get('genre', '')
    artist_filter = request.GET.get('artist', '')
    page_size = request.GET.get('page_size', '12')
    try:
        page_size = int(page_size)
        if page_size not in [6, 12, 24]:
            page_size = 12
    except (ValueError, TypeError):
        page_size = 12

    tracks = Track.objects.filter(status=Track.STATUS_APPROVED).select_related('album').prefetch_related('artists', 'genres')
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
    paginator = Paginator(tracks, page_size)
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
        'page_size': page_size,
    }
    return render(request, 'home.html', context)

@login_required
def upload_page(request):
    if request.method == 'POST':
        form = TrackUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, 'Трек успешно загружен!')
            return redirect('my_tracks')
    else:
        form = TrackUploadForm()
    genres = Genre.objects.all()
    return render(request, 'upload.html', {'form': form, 'genres': genres})

@login_required
def my_tracks(request):
    tracks = Track.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')
    paginator = Paginator(tracks, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'my_tracks.html', {'page_obj': page_obj})


@login_required
def delete_track(request, track_id):
    track = get_object_or_404(Track, id=track_id)
    if track.uploaded_by != request.user:
        messages.error(request, "Вы можете удалять только свои треки.")
        return redirect('my_tracks')
    track.delete()
    messages.success(request, "Трек удалён.")
    return redirect('my_tracks')