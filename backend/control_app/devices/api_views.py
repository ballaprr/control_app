from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Device
from .serializers import DeviceSerializer, DeviceListSerializer
from arena.models import Arena


class DeviceListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DeviceSerializer
        return DeviceListSerializer
    
    def get_queryset(self):
        queryset = Device.objects.all()
        arena_id = self.request.query_params.get('arena_id')
        if arena_id:
            queryset = queryset.filter(arena_id=arena_id)
        return queryset


class DeviceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def devices_by_arena(request, arena_id):
    """Get all devices for a specific arena"""
    try:
        arena = Arena.objects.get(id=arena_id)
    except Arena.DoesNotExist:
        return Response({'error': 'Arena not found'}, status=status.HTTP_404_NOT_FOUND)
    
    devices = Device.objects.filter(arena=arena)
    serializer = DeviceListSerializer(devices, many=True)
    
    return Response({
        'arena_name': arena.arena_name,
        'devices': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reboot_device(request):
    """Reboot a specific device"""
    device_id = request.data.get('device_id')
    
    if not device_id:
        return Response({'error': 'Device ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        device = Device.objects.get(device_id=device_id)
    except Device.DoesNotExist:
        return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user has control of the arena
    if device.arena.active_controller != request.user:
        return Response({'error': 'You are not controlling this arena'}, status=status.HTTP_403_FORBIDDEN)
    
    # Here you would implement the actual device reboot logic
    # For now, we'll just return a success message
    
    return Response({
        'message': f'Device {device.name} (ID: {device.device_id}) reboot initiated',
        'device': DeviceSerializer(device).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def trigger_device_action(request):
    """Trigger an action on a specific device"""
    device_id = request.data.get('device_id')
    action = request.data.get('action')
    
    if not device_id or not action:
        return Response({'error': 'Device ID and action are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        device = Device.objects.get(device_id=device_id)
    except Device.DoesNotExist:
        return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user has control of the arena
    if device.arena.active_controller != request.user:
        return Response({'error': 'You are not controlling this arena'}, status=status.HTTP_403_FORBIDDEN)
    
    # Here you would implement the actual device action logic
    # For now, we'll just return a success message
    
    return Response({
        'message': f'Action "{action}" triggered on device {device.name} (ID: {device.device_id})',
        'device': DeviceSerializer(device).data,
        'action': action
    }, status=status.HTTP_200_OK)
