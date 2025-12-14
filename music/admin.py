from django.contrib import admin
from .models import Artist, Album, Track, Comment

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'year')
    search_fields = ('title', 'artists__name')
    filter_horizontal = ('artists',)  # удобный виджет для M2M

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at', 'album', 'genre')
    list_filter = ('genre', 'uploaded_at')
    search_fields = ('title', 'artists__name', 'uploaded_by')
    filter_horizontal = ('artists',)  # удобный виджет для M2M

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('track', 'author_name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('track__title', 'author_name')