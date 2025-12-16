from django import forms
from django.core.exceptions import ValidationError
from .models import Track, Artist, Album, Genre

class GenreMultiField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['to_field_name'] = 'code'
        super().__init__(*args, **kwargs)

    def validate(self, value):
        super().validate(value)
        if len(value) != len(set(value)):
            raise ValidationError("Нельзя выбрать один жанр дважды.")

class TrackUploadForm(forms.ModelForm):
    artist_names = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    album_title = forms.CharField(
        max_length=200,
        required=False,
        label="Альбом",
        widget=forms.TextInput(attrs={'placeholder': 'Название альбома', 'id': 'album-input'})
    )
    genres = GenreMultiField(
        queryset=Genre.objects.all(),
        required=False,
        label="Жанры"
    )

    class Meta:
        model = Track
        fields = ['title', 'audio_file', 'uploaded_by', 'album_title', 'artist_names', 'genres']
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

        if commit:
            track.save()
            # Теперь track имеет id — можно добавлять ManyToMany
            artist_names_str = self.cleaned_data.get('artist_names')
            if artist_names_str:
                artist_names = [name.strip() for name in artist_names_str.split('|') if name.strip()]
                for name in artist_names:
                    artist, _ = Artist.objects.get_or_create(name=name)
                    track.artists.add(artist)

            album_title = self.cleaned_data.get('album_title')
            if album_title:
                album, _ = Album.objects.get_or_create(title=album_title.strip())
                track.album = album

            self.save_m2m()

        return track