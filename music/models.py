# music/models.py
from django.db import models

class Artist(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя исполнителя")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Исполнитель"
        verbose_name_plural = "Исполнители"


class Album(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название альбома")
    year = models.PositiveIntegerField(verbose_name="Год выпуска", null=True, blank=True)
    artists = models.ManyToManyField(Artist, related_name="albums", verbose_name="Исполнители")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Альбом"
        verbose_name_plural = "Альбомы"


class Track(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название трека")
    audio_file = models.FileField(upload_to='tracks/', verbose_name="Аудиофайл")
    uploaded_by = models.CharField(max_length=100, verbose_name="Ник загрузившего")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Альбом")
    artists = models.ManyToManyField(Artist, related_name="tracks", verbose_name="Исполнители")
    genre = models.CharField(max_length=50, blank=True, verbose_name="Жанр")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Трек"
        verbose_name_plural = "Треки"


class Comment(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name="comments", verbose_name="Трек")
    author_name = models.CharField(max_length=100, verbose_name="Имя автора комментария")
    text = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")

    def __str__(self):
        return f"Комментарий от {self.author_name} к {self.track.title}"

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"