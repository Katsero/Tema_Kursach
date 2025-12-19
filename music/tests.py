from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Track, Artist, Album, Genre, Comment
from .forms import TrackUploadForm


class ModelTestCase(TestCase):
    """Тесты моделей"""

    def setUp(self):
        # Используем get_or_create, чтобы не нарушать уникальность
        self.genre, _ = Genre.objects.get_or_create(name="Рок", code="rock")
        self.artist, _ = Artist.objects.get_or_create(name="Кипелов")
        self.album, _ = Album.objects.get_or_create(title="Атака")
        self.album.artists.add(self.artist)

    def test_genre_str(self):
        self.assertEqual(str(self.genre), "Рок")

    def test_artist_str(self):
        self.assertEqual(str(self.artist), "Кипелов")

    def test_album_str(self):
        self.assertEqual(str(self.album), "Атака")

    def test_track_defaults(self):
        track = Track.objects.create(
            audio_file=SimpleUploadedFile("test.mp3", b"fake audio content"),
        )
        self.assertEqual(track.title, "Unnamed")
        self.assertEqual(track.uploaded_by, "Аноним")

    def test_track_with_relations(self):
        track = Track.objects.create(
            title="Песня",
            uploaded_by="Юзер",
            audio_file=SimpleUploadedFile("song.mp3", b"audio"),
            album=self.album,
        )
        track.artists.add(self.artist)
        track.genres.add(self.genre)
        self.assertIn(self.artist, track.artists.all())
        self.assertIn(self.genre, track.genres.all())
        self.assertEqual(track.album, self.album)

    def test_comment(self):
        track = Track.objects.create(audio_file=SimpleUploadedFile("t.mp3", b"x"))
        comment = Comment.objects.create(
            track=track,
            author_name="Гость",
            text="Круто!"
        )
        self.assertEqual(str(comment), "Комментарий от Гость к Unnamed")


class FormTestCase(TestCase):
    """Тесты формы загрузки трека"""

    def test_valid_form(self):
        audio = SimpleUploadedFile("valid.mp3", b"fake mp3", content_type="audio/mpeg")
        form_data = {
            'title': 'Тест',
            'uploaded_by': 'Тестер',
            'artist_names': 'Кино|Наутилус',
            'album_title': 'Группа крови',
            'genres': ['rock'],
        }
        files = {'audio_file': audio}
        form = TrackUploadForm(data=form_data, files=files)
        self.assertTrue(form.is_valid())

    def test_invalid_file_extension(self):
        bad_file = SimpleUploadedFile("bad.txt", b"not audio", content_type="text/plain")
        form = TrackUploadForm(files={'audio_file': bad_file})
        self.assertFalse(form.is_valid())
        self.assertIn("Поддерживаются только .mp3 и .wav файлы.", form.errors['audio_file'])

    def test_file_too_large(self):
        large_file = SimpleUploadedFile("big.mp3", b"x" * (21 * 1024 * 1024))
        form = TrackUploadForm(files={'audio_file': large_file})
        self.assertFalse(form.is_valid())
        self.assertIn("Файл должен быть не больше 20 МБ.", form.errors['audio_file'])


class ViewTestCase(TestCase):
    """Тесты основных view (home и upload)"""

    def setUp(self):
        self.client = Client()
        # Используем существующие жанры из миграции
        self.genre, _ = Genre.objects.get_or_create(name="Поп", code="pop")
        self.artist, _ = Artist.objects.get_or_create(name="Земфира")
        self.track = Track.objects.create(
            title="Прости",
            audio_file=SimpleUploadedFile("track.mp3", b"fake"),
        )
        self.track.artists.add(self.artist)
        self.track.genres.add(self.genre)

    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Анонимная музыкальная библиотека")
        self.assertContains(response, "Прости")

    def test_search_filter(self):
        response = self.client.get(reverse('home'), {'search': 'Прости'})
        self.assertContains(response, "Прости")
        self.assertNotContains(response, "Неизвестный трек")

    def test_upload_page_get(self):
        response = self.client.get(reverse('upload'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Загрузить трек")

    def test_upload_page_post_success(self):
        audio = SimpleUploadedFile("new.mp3", b"test audio", content_type="audio/mpeg")
        response = self.client.post(reverse('upload'), {
            'title': 'Новый трек',
            'uploaded_by': 'Анон',
            'artist_names': 'Король и Шут',
            'album_title': 'Как в старой сказке',
            'genres': ['rock'],
            'audio_file': audio,
        })
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(Track.objects.filter(title="Новый трек").exists())


class APITestCase(TestCase):
    """Тесты DRF API"""

    def setUp(self):
        self.client = Client()
        self.artist, _ = Artist.objects.get_or_create(name="DDT")

    def test_artists_api(self):
        response = self.client.get(reverse('artist-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DDT")

    def test_autocomplete_artists(self):
        response = self.client.get(reverse('autocomplete-artists'), {'q': 'DDT'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "DDT")