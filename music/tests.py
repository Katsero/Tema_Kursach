from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Track, Artist, Album, Genre, Comment, CustomUser


class ModelTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(email="test@test.com", username="anon")
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
            audio_file=SimpleUploadedFile("test.mp3", b"fake"),
            uploaded_by=self.user,
            status='approved'
        )
        self.assertEqual(track.title, "Unnamed")

    def test_track_with_relations(self):
        track = Track.objects.create(
            title="Песня",
            uploaded_by=self.user,
            audio_file=SimpleUploadedFile("song.mp3", b"audio"),
            album=self.album,
            status='approved'
        )
        track.artists.add(self.artist)
        track.genres.add(self.genre)
        self.assertIn(self.artist, track.artists.all())
        self.assertIn(self.genre, track.genres.all())

    def test_comment(self):
        track = Track.objects.create(
            audio_file=SimpleUploadedFile("t.mp3", b"x"),
            uploaded_by=self.user,
            status='approved'
        )
        comment = Comment.objects.create(
            track=track,
            author_name="Гость",
            text="Круто!"
        )
        self.assertIn("Гость", str(comment))


class ViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create(email="user@test.com", username="user")
        self.genre, _ = Genre.objects.get_or_create(name="Поп", code="pop")
        self.artist, _ = Artist.objects.get_or_create(name="Земфира")
        self.track = Track.objects.create(
            title="Прости",
            uploaded_by=self.user,
            audio_file=SimpleUploadedFile("track.mp3", b"fake"),
            status='approved' 
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

    def test_upload_page_requires_login(self):
        response = self.client.get(reverse('upload'))
        self.assertEqual(response.status_code, 302) 

    def test_upload_as_logged_in_user(self):
        self.client.force_login(self.user)
        audio = SimpleUploadedFile("new.mp3", b"test", content_type="audio/mpeg")
        response = self.client.post(reverse('upload'), {
            'title': 'Новый трек',
            'artist_names': 'Король и Шут',
            'album_title': 'Сказка',
            'genres': ['pop'],
            'audio_file': audio,
        })
        self.assertRedirects(response, reverse('my_tracks'))
        self.assertTrue(Track.objects.filter(title="Новый трек").exists())


class APITestCase(TestCase):
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
