from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView 



class AuthAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            try:
                token = Token.objects.get(user=user)
            except:
                token = Token.objects.create(user=user)
            return Response(data={'key': token.key})
        return Response(status=status.HTTP_401_UNAUTHORIZED)
           
 
    

@api_view(['POST'])
def registration_api_view(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data.get('username')
    password = serializer.validated_data.get('password')

    user = User.objects.create_user(
        username=username,
        password=password,
        is_active=True
    )

    return Response(
        status=status.HTTP_201_CREATED,
        data={'user_id': user.id}
    )

