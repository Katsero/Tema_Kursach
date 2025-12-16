# music/admin.py
from django.contrib import admin
from .models import Artist, Album, Track, Comment, Genre

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'year')
    search_fields = ('title', 'artists__name')
    filter_horizontal = ('artists',)

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at', 'album', 'get_genres_display')
    list_filter = ('uploaded_at', 'genres')
    search_fields = ('title', 'artists__name', 'uploaded_by', 'genres__name')
    filter_horizontal = ('artists', 'genres')

    def get_genres_display(self, obj):
        return ", ".join([g.name for g in obj.genres.all()]) or "Не указаны"
    get_genres_display.short_description = "Жанры"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('track', 'author_name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('track__title', 'author_name')