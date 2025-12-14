# music/forms.py
from django import forms
from .models import Track

class TrackUploadForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ['title', 'audio_file', 'uploaded_by', 'album', 'genre']
        widgets = {
            'uploaded_by': forms.TextInput(attrs={'placeholder': 'Ваш ник'}),
            'title': forms.TextInput(attrs={'placeholder': 'Название трека'}),
            'genre': forms.TextInput(attrs={'placeholder': 'Жанр (например: рок, поп)'}),
        }