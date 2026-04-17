from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Director, Film, Genre
from rest_framework import status
from .serializers import (
    FilmListSerializer,
    FilmDetailSerializer,
    FilmValidateSerializer,
    GenreSerializer,
    DirectorSerializer,
    DirectorCreateSerializer
)
from django.db import transaction
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
    )


from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet

class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'total': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })
 
class GenreListAPIView(ListCreateAPIView):
    queryset = Genre.objects.all()           #list of data
    serializer_class = GenreSerializer       #serializer inherited by ModelSerializer
    pagination_class = CustomPagination



class GenreDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'id'



class DirectorViewSet(ModelViewSet):
    queryset = Director.objects.all()
    serializer_class = DirectorSerializer
    pagination_class = CustomPagination
    lookup_field = 'id'


    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT']:
            return DirectorCreateSerializer
        return DirectorSerializer

    




@api_view(['GET', 'PUT', 'DELETE'])
def film_detail_api_view(request, id):
    try:
        film = Film.objects.get(id=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        data = FilmDetailSerializer(film, many=False).data
        return Response(data=data)
    elif request.method == 'DELETE':
        film.delete()
        return Response(status=status .HTTP_204_NO_CONTENT)
    elif request.method == 'PUT':

        serializer = FilmValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        film.title = serializer.validated_data.get('title')
        film.text = serializer.validated_data.get('text')
        film.release_year = serializer.validated_data.get('release_year')
        film.rating = serializer.validated_data.get('rating')
        film.is_hit = serializer.validated_data.get('is_hit')
        film.director_id = serializer.validated_data.get('director_id')
        film.genres.set(serializer.validated_data.get('genres'))
        film.save()
        return Response(status=status.HTTP_201_CREATED,
                        data=FilmDetailSerializer(film).data)



@api_view(['GET', 'POST'])
def film_list_api_view(request):
    if request.method == 'GET':
        # step 1: collect films (QuerySet)
        films = Film.objects.select_related('director').prefetch_related('genres', 'reviews').all()

        # step 2: reformat films to list of dictionaries
        data = FilmListSerializer(films, many=True).data

        # step 3: return responce
        return Response(data) #data = dictionary, list, list of dictionaries
    elif request.method == 'POST':
        # step 0: Validation (Existing, Typing, Extra)
        serializer = FilmValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=serializer.errors)
        # step 1: receive data
        title = serializer.validated_data.get('title')
        text = serializer.validated_data.get('text')
        release_year = serializer.validated_data.get('release_year')
        rating = serializer.validated_data.get('rating')
        is_hit = serializer.validated_data.get('is_hit')  # "y"
        director_id = serializer.validated_data.get('director_id')
        genres = serializer.validated_data.get('genres')
       
        # step 2: create film
        with transaction.atomic():
            film = Film.objects.create(
                title=title,
                text=text,
                rating=rating,
                release_year=release_year,
                is_hit=is_hit,
                director_id=director_id,
            )
            film.genres.set(genres)
            film.save()

        # step 3: return response
        return Response(status=status.HTTP_201_CREATED,
                        data=FilmDetailSerializer(film).data)