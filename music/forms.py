# music/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Track, Artist, Album, Genre

class GenreMultiWidget(forms.SelectMultiple):
    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.attrs = {'class': 'genre-select hidden'}

class GenreMultiField(forms.ModelMultipleChoiceField):
    def validate(self, value):
        super().validate(value)
        if len(value) != len(set(value)):
            raise ValidationError("Нельзя выбрать один жанр дважды.")

class TrackUploadForm(forms.ModelForm):
    artist_name = forms.CharField(
        max_length=100,
        required=False,
        label="Исполнитель",
        widget=forms.TextInput(attrs={'placeholder': 'Например: Кипелов', 'id': 'artist-input'})
    )
    album_title = forms.CharField(
        max_length=200,
        required=False,
        label="Альбом",
        widget=forms.TextInput(attrs={'placeholder': 'Название альбома', 'id': 'album-input'})
    )
    # Поле жанров — скрытое, управляем через JS
    genres = GenreMultiField(
        queryset=Genre.objects.all(),
        widget=GenreMultiWidget(),
        required=False,
        label="Жанры"
    )

    class Meta:
        model = Track
        fields = ['title', 'audio_file', 'uploaded_by', 'album_title', 'artist_name', 'genres']
        widgets = {
            'uploaded_by': forms.TextInput(attrs={'placeholder': 'Ваш ник (по умолчанию: Аноним)'}),
            'title': forms.TextInput(attrs={'placeholder': 'Название трека (по умолчанию: Unnamed)'}),
        }

    def clean_audio_file(self):
        file = self.cleaned_data.get('audio_file')
        if file:
            ext = file.name.split('.')[-1].lower()
            if ext not in ['mp3', 'wav']:
                raise forms.ValidationError("Поддерживаются только .mp3 и .wav файлы.")
            if file.size > 20 * 1024 * 1024:
                raise forms.ValidationError("Файл должен быть не больше 20 МБ.")
        return file

    def save(self, commit=True):
        track = super().save(commit=False)

        artist_name = self.cleaned_data.get('artist_name')
        if artist_name:
            artist, _ = Artist.objects.get_or_create(name=artist_name.strip())
            track.artists.add(artist)

        album_title = self.cleaned_data.get('album_title')
        if album_title:
            album, _ = Album.objects.get_or_create(title=album_title.strip())
            track.album = album

        if commit:
            track.save()
            self.save_m2m()

        return track