from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, CustomerProfile, CaregiverProfile
from .serializers import (
    UserRegistrationSerializer, UserSerializer, 
    CustomerProfileSerializer, CaregiverProfileSerializer, LoginSerializer
)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        if user.user_type == 'customer':
            profile, created = CustomerProfile.objects.get_or_create(user=user)
            return profile
        elif user.user_type == 'caregiver':
            profile, created = CaregiverProfile.objects.get_or_create(user=user)
            return profile
        return None
    
    def get_serializer_class(self):
        user = self.request.user
        if user.user_type == 'customer':
            return CustomerProfileSerializer
        elif user.user_type == 'caregiver':
            return CaregiverProfileSerializer
        return None