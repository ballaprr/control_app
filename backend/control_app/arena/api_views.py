from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Arena
from .serializers import ArenaSerializer, ArenaListSerializer


class ArenaListCreateView(generics.ListCreateAPIView):
    queryset = Arena.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArenaSerializer
        return ArenaListSerializer


class ArenaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Arena.objects.all()
    serializer_class = ArenaSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def take_control(request, arena_id):
    """Allow a user to take control of an arena"""
    try:
        arena = Arena.objects.get(id=arena_id)
    except Arena.DoesNotExist:
        return Response({'error': 'Arena not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Update the active controller
    arena.active_controller = request.user
    arena.save()
    
    serializer = ArenaSerializer(arena)
    return Response({
        'message': f'You are now controlling {arena.arena_name}',
        'arena': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def release_control(request, arena_id):
    """Allow a user to release control of an arena"""
    try:
        arena = Arena.objects.get(id=arena_id)
    except Arena.DoesNotExist:
        return Response({'error': 'Arena not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Only allow the current controller to release control
    if arena.active_controller != request.user:
        return Response({'error': 'You are not controlling this arena'}, status=status.HTTP_403_FORBIDDEN)
    
    arena.active_controller = None
    arena.save()
    
    serializer = ArenaSerializer(arena)
    return Response({
        'message': f'You have released control of {arena.arena_name}',
        'arena': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_brightness(request, arena_id):
    """Update arena brightness"""
    try:
        arena = Arena.objects.get(id=arena_id)
    except Arena.DoesNotExist:
        return Response({'error': 'Arena not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Only allow the current controller to update brightness
    if arena.active_controller != request.user:
        return Response({'error': 'You are not controlling this arena'}, status=status.HTTP_403_FORBIDDEN)
    
    brightness = request.data.get('brightness')
    if brightness is None:
        return Response({'error': 'Brightness value is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        brightness = int(brightness)
        if brightness < 0 or brightness > 100:
            return Response({'error': 'Brightness must be between 0 and 100'}, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
        return Response({'error': 'Brightness must be a valid integer'}, status=status.HTTP_400_BAD_REQUEST)
    
    arena.brightness = brightness
    arena.save()
    
    serializer = ArenaSerializer(arena)
    return Response({
        'message': f'Brightness updated to {brightness}%',
        'arena': serializer.data
    }, status=status.HTTP_200_OK)
