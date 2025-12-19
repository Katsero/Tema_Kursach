from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Artist, Album, Track, Comment, Genre

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_moderator', 'is_active', 'date_joined')
    list_filter = ('is_moderator', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'username')}),
        ('Разрешения', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'is_moderator'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_moderator', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

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