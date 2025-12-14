# music/forms.py
from django import forms
from .models import Track, Artist, Album

class TrackUploadForm(forms.ModelForm):
    artist_name = forms.CharField(
        max_length=100,
        required=False,
        label="Исполнитель (введите имя или выберите из списка)",
        widget=forms.TextInput(attrs={'placeholder': 'Например: Кипелов', 'id': 'artist-input'})
    )
    album_title = forms.CharField(
        max_length=200,
        required=False,
        label="Альбом (необязательно)",
        widget=forms.TextInput(attrs={'placeholder': 'Название альбома', 'id': 'album-input'})
    )

    class Meta:
        model = Track
        fields = ['title', 'audio_file', 'uploaded_by', 'album_title', 'artist_name', 'genre']
        widgets = {
            'uploaded_by': forms.TextInput(attrs={'placeholder': 'Ваш ник (по умолчанию: Аноним)'}),
            'title': forms.TextInput(attrs={'placeholder': 'Название трека (по умолчанию: Unnamed)'}),
            'genre': forms.Select(choices=Track.GENRE_CHOICES),
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
            artist, created = Artist.objects.get_or_create(name=artist_name.strip())
            track.artists.add(artist)

        album_title = self.cleaned_data.get('album_title')
        if album_title:
            album, created = Album.objects.get_or_create(title=album_title.strip())
            track.album = album

        if commit:
            track.save()
            self.save_m2m()

        return track