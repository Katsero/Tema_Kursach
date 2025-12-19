from rest_framework import serializers
from .models import Artist, Album, Track, Comment

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'

class AlbumSerializer(serializers.ModelSerializer):
    artists = ArtistSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = '__all__'

class TrackSerializer(serializers.ModelSerializer):
    artists = ArtistSerializer(many=True, read_only=True)
    album = AlbumSerializer(read_only=True)

    class Meta:
        model = Track
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'