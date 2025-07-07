from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .models import UserProfile
from .serializers import UserSerializer, UserProfileSerializer
from .utils import get_tokens_for_user

class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create user profile
        UserProfile.objects.create(
            user=user,
            target_language=request.data.get('target_language', 'EN'),
            current_level=request.data.get('current_level', 'A1'),
            learning_goal=request.data.get('learning_goal', 'CASUAL'),
            daily_goal_minutes=request.data.get('daily_goal_minutes', 15)
        )

        tokens = get_tokens_for_user(user)
        return Response({
            'user': serializer.data,
            **tokens,
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            tokens = get_tokens_for_user(user)
            return Response(tokens)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user.profile 