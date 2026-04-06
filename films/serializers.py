from rest_framework import serializers
from .models import Film, Director


class DirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = 'id fio'.split()


class FilmListSerializer(serializers.ModelSerializer):
    director = DirectorSerializer(many=False)
    genres = serializers.SerializerMethodField()

    class Meta:
        model = Film
        fields = 'id title release_year is_hit director genres reviews'.split()
        depth = 1 
        # Выдает данные, все данные в базе
    
    def get_genres(self, film):
        # list_ = []
        # for i in film.genres.all():
        #     list_.append(i.name)
        # return list_
        return film.genre_list()[0:2]


class FilmDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = '__all__'