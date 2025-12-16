from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from arena.models import Arena, User
from devices.models import Device
from django.utils.timezone import now
from django.http import JsonResponse
import requests
import json
import os
from django.views.decorators.csrf import csrf_exempt
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework import status

load_dotenv()

"""
TILE_DEVICE_MAP = {
    "a": [39353, 39354, None, None],
    "b": [39265, 39262, 39266, 39264], 
    "c": [None, None, None, None],
    "d": [None, None, None, None, None, 39265, 39262],
    "e": [39266, 39264, None, None, None, None, None],
    "0": [39353, 39354, None, None, None, 39265, 39262, 39266, 39264, None, None, None, None, None]
}

TILE_DEVICE_MAP = {
    "a": [39353, 39354, 39357, 39358],
    "b": [39268, 39269, 39270, 39271],
    "c": [39272, 39274, 39277, 39278],
    "d": [39353, 39354, 39357, 39358, 39268, 39269],
    "e": [39270, 39271, 39272, 39274, 39277, 39278],
    "0": [39353, 39354, 39357, 39358, 39268, 39269, 39270, 39271, 39272, 39274, 39277, 39278],
}
"""
TILE_DEVICE_MAP = {}

payload_map = {
    "17": ["17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30"],
    "18": ["31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44"],
    "19": ["45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58"],
    "20": ["59", "60", "61", "62"],
    "21": ["63", "64", "65", "66"],
    "22": ["67", "68", "69", "70"],
    "23": ["71", "72", "73", "74", "75", "76", "77"],
    "24": ["78", "79", "80", "81", "82", "83", "84"],
}

@login_required
def dashboard_view(request):
    # Check if user is logged in
    if not request.user.is_authenticated:
        return redirect('user:login')  # Redirect to login if not authenticated

    # Fetch the user's selected arena
    arena = request.session.get('arena_id')  # Assuming the user is an arena (AbstractUser)
    # Query devices for the user's arena
    devices = Device.objects.filter(arena=arena)

    label_to_device = {device.tile_label: device.device_id for device in devices}
    # Populate TILE_DEVICE_MAP with tile_label and device_id
    
    tile_mappings = {
        "a": ["A1", "A2", "A3", "A4"],
        "b": ["A6", "A7", "A8", "A9"],
        "c": ["A11", "A12", "A13", "A14"],
        "d": ["A1", "A2", "A3", "A4", "A5", "A6", "A7"],
        "e": ["A8", "A9", "A10", "A11", "A12", "A13", "A14"],
        "0": ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12", "A13", "A14"],
    }

    # Populate TILE_DEVICE_MAP
    for key, labels in tile_mappings.items():
        TILE_DEVICE_MAP[key] = [
            label_to_device.get(label, None)  # Replace label with device_id or None if not found
            for label in labels
        ]

    print(TILE_DEVICE_MAP)
    # Redirect to the control view
    return redirect('control_view')


def fetch_legend_data(request, setup_id):
    # first output_data has the trigger & asset_id
    # setup_id = request.GET.get("setup_id", 254745)
    api_1_url = 'https://info-beamer.com/api/v1/setup/' + str(setup_id) + '/'
    output_data = []
    try:
        response_1 = requests.get(api_1_url, auth=('', os.getenv("API_KEY")))
        response_1.raise_for_status()
        data_1 = response_1.json()
        for schedule in data_1["config"][""]["schedules"]:
            for page in schedule.get("pages", []):
                interaction = page.get("interaction", {})
                trigger = interaction.get("remote")
                for tile in page.get("tiles", []):
                    asset_id = tile.get("asset")
                    output_data.append({
                        "trigger": trigger,
                        "asset_id": asset_id
                    })

    except requests.exceptions.RequestException as e:
        output_data = []

    # second output_data includes thumb
    api_2_url = 'https://info-beamer.com/api/v1/asset/list'
    try:
        response_2 = requests.get(api_2_url, auth=('', os.getenv("API_KEY")))
        response_2.raise_for_status()
        data_2 = response_2.json()
        assets_data = data_2.get("assets", [])
    except requests.exceptions.RequestException as e:
        assets_data = []

    for item in output_data:
        asset_id = item["asset_id"]
        for asset in assets_data:
            if asset["id"] == asset_id:
                item["thumb"] = asset.get("thumb")
                break

    return output_data


def get_setups(request):
    try:
        response = requests.get("https://info-beamer.com/api/v1/setup/list", auth=('', os.getenv("API_KEY")))
        if response.status_code == 200:
            setups = response.json()
            ids = [(item.get("id"), item.get("name")) for item in setups['setups']]
            return ids
        else:
            return JsonResponse({"error": "Failed to get setups"}, status=500)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": "Failed to get setups"}, status=500)

# function is called when page is reloaded
@login_required
def control_view(request):
    # Get current time in military format (HH:MM:SS)
    triggers_to_replace = ['59', '60', '61', '62']
    current_time = now().strftime("%H:%M:%S")  # Ensures military time format
    output_data = fetch_legend_data(request, 254745)
    ids = get_setups(request)
    active_controller = Arena.objects.get(id=request.session.get('arena_id')).active_controller
    return render(request, 'dashboard/index.html', {
        'output_data': output_data,       # Pass the output data to the template
        'current_time': current_time,  # Pass the current time to the template
        'tile_range': range(1, 15),      # Send range from 1 to 14 for tiles
        'triggers_to_replace': triggers_to_replace,
        'ids': ids,
        'active_controller': active_controller,
    })

def fetch_legend_data_api(request, setup_id):
    output_data = fetch_legend_data(request, setup_id)
    return JsonResponse(output_data, safe=False)

@api_view(['GET'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def device_output(request, title_Index):
    
    try:
        # Get the current arena from query parameters OR session (for legacy dashboard)
        arena_id = request.GET.get('arena_id') or request.session.get('arena_id')
        if not arena_id:
            return JsonResponse({"error": "No arena_id provided"}, status=400)
        
        # Populate TILE_DEVICE_MAP for current arena
        devices = Device.objects.filter(arena_id=arena_id)
        label_to_device = {device.tile_label: device.device_id for device in devices}
        
        # Create mapping for all tiles A1-A14
        tile_labels = [f"A{i}" for i in range(1, 15)]
        device_ids = [label_to_device.get(label, None) for label in tile_labels]
        
        # Get device for the specific tile
        index = int(title_Index) - 1
        if index < 0 or index >= len(device_ids):
            return JsonResponse({"error": "Invalid tile index"}, status=400)
            
        device_id = device_ids[index]
        if not device_id:
            return JsonResponse({"error": f"No device registered for tile A{title_Index}"}, status=404)
          
        print(f"Fetching output for device {device_id} (tile A{title_Index})")
        response = requests.get(f"https://info-beamer.com/api/v1/device/{device_id}/output", auth=('', os.getenv("API_KEY")))
        print(f"Info beamer response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            if isinstance(data, dict) and 'src' in data:
                print(f"Image data length: {len(data['src']) if data['src'] else 0}")
            return JsonResponse(data, status=200)
        else:
            print(f"Error response: {response.text}")
            return JsonResponse({"error": f"Failed to get output for device {device_id}"}, status=500)
            
    except (ValueError, IndexError):
        return JsonResponse({"error": "Invalid index"}, status=400)
    
        

@csrf_exempt
def reboot_device(request):
    arena_id = request.session.get('arena_id')
    if not arena_id:
        return JsonResponse({"error": "No arena in session"}, status=400)
    
    try:
        arena = Arena.objects.get(id=arena_id)
        if arena.active_controller != request.user:
            return JsonResponse({"error": "You are not the active controller"}, status=403)
    except Arena.DoesNotExist:
        return JsonResponse({"error": "Arena not found"}, status=404)
    
    if request.method == "POST":
        api_key = os.getenv("API_KEY")
        data = json.loads(request.body)
        index = data.get("tile")
        
        # Get device from database instead of global map
        tile_label = f"A{index}"
        try:
            device = Device.objects.get(arena_id=arena_id, tile_label=tile_label)
            device_id = device.device_id
        except Device.DoesNotExist:
            return JsonResponse({"error": f"No device registered for tile {tile_label}"}, status=404)
        
        response = requests.post(f"https://info-beamer.com/api/v1/device/{device_id}/reboot", auth=('', api_key))
        if response.status_code == 200:
            return JsonResponse({"status": "Device rebooted successfully"}, status=200)
        else:
            return JsonResponse({"error": "Failed to reboot device"}, status=500)

@csrf_exempt
def blackscreen(request):
    arena_id = request.session.get('arena_id')
    if not arena_id:
        return JsonResponse({"error": "No arena in session"}, status=400)
    
    try:
        arena = Arena.objects.get(id=arena_id)
        if arena.active_controller != request.user:
            return JsonResponse({"error": "You are not the active controller"}, status=403)
    except Arena.DoesNotExist:
        return JsonResponse({"error": "Arena not found"}, status=404)
    
    if request.method == "POST":
        api_key = os.getenv("API_KEY")
        
        # Get all device IDs for this arena from database
        devices = Device.objects.filter(arena_id=arena_id)
        device_ids = [device.device_id for device in devices]
        
        if not device_ids:
            return JsonResponse({"error": "No devices registered for this arena"}, status=404)

        def send_request(device_id):
            url = f'https://info-beamer.com/api/v1/device/{device_id}/node/root/remote/trigger/'
            response = requests.post(url, data={"data": "m"}, auth=('', api_key))
            return {"device_id": device_id, "status": response.status_code}
        
        with ThreadPoolExecutor() as executor:
                responses = list(executor.map(send_request, device_ids))

        responses = [response for response in responses if response is not None]

        return JsonResponse({"results": responses}, status=200)
    
@csrf_exempt
@api_view(['POST'])
def takecontrol(request):
    user = request.user
    arena_id = request.session.get('arena_id')
    if not arena_id:
        return Response({"error": "Arena ID not found in session"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        arena = Arena.objects.get(id=arena_id)
        if arena.active_controller is None:
            arena.active_controller = user
            arena.save()
        elif arena.active_controller == user:
            arena.active_controller = None
            arena.save()
        else:
            return Response({"error": "Arena is already controlled by another user"}, status=status.HTTP_403_FORBIDDEN)
        return Response({"status": "Active controller updated successfully"}, status=status.HTTP_200_OK)
    except Arena.DoesNotExist:
        return Response({"error": "Arena not found"}, status=status.HTTP_404_NOT_FOUND)
    

          
@csrf_exempt
def get_deviceid(request, tileIndex):
    arena_id = request.session.get('arena_id')
    if not arena_id:
        return JsonResponse({"error": "No arena in session"}, status=400)
    
    try:
        arena = Arena.objects.get(id=arena_id)
        if arena.active_controller != request.user:
            return JsonResponse({"error": "You are not the active controller"}, status=403)
    except Arena.DoesNotExist:
        return JsonResponse({"error": "Arena not found"}, status=404)
    
    try:
        api_key = os.getenv("API_KEY")
        tile_label = f"A{tileIndex}"
        
        # Get device from database instead of global map
        try:
            device = Device.objects.get(arena_id=arena_id, tile_label=tile_label)
            device_id = device.device_id
        except Device.DoesNotExist:
            return JsonResponse({"error": f"No device registered for tile {tile_label}"}, status=404)
        
        response = requests.get(f"https://info-beamer.com/api/v1/device/{device_id}/sensor", auth=('', api_key))
        response = response.json()
        response = {'boot_uptime': response['boot']['uptime'], 'cpu idle': response['cpu']['idle'], 'disk available': response['disk']['available'],
                    'disk used': response['disk']['used'], 'fps': response['info_beamer']['fps'], 'info beamer uptime': response['info_beamer']['uptime'],
                    'info beamer version': response['info_beamer']['version'], 'hwids eth0': response['hwids']['eth0'], 'hwids wlan0': response['hwids']['wlan0'],
                    'network data received': response['net']['data']['received'], 'network data sent': response['net']['data']['sent'], 'network ip address': response['net']['ip'], 
                    'network mac address': response['net']['mac'], 'video hz': response['video']['hz'], 'video resolution': response['video']['resolution'], 'gpu': response['ram']['gpu'],
                    'gpu_used': response['ram']['gpu_used'], 'gpu arm': response['ram']['arm'], 'revision': response['pi']['revision'], 'PI CPU temperature': response['temp']}
        if response:
           return JsonResponse(response, status=200)
        else:
            return JsonResponse({"error": f"Failed to get output for device {device_id}"}, status=500)
            
    except (ValueError, IndexError):
        return JsonResponse({"error": "Invalid index"}, status=400)

@csrf_exempt
def trigger_action_legacy(request):
    """Legacy trigger action for Django template - uses session auth"""
    import time
    
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    api_key = os.getenv("API_KEY")
    if not api_key:
        return JsonResponse({"error": "API key is missing"}, status=500)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    arena_id = request.session.get('arena_id')
    zone = data.get("zone") or data.get("tile")
    payload = data.get("payload")
    
    if not arena_id:
        return JsonResponse({"error": "No arena in session"}, status=400)
    
    if not zone or not payload:
        return JsonResponse({"error": "Missing zone/tile or payload"}, status=400)
    
    # Check if user has control of the arena
    try:
        arena = Arena.objects.get(id=arena_id)
        if arena.active_controller != request.user:
            return JsonResponse({"error": "You are not the active controller"}, status=403)
    except Arena.DoesNotExist:
        return JsonResponse({"error": "Arena not found"}, status=404)

    try:
        payload_int = int(payload)
    except ValueError:
        return JsonResponse({"error": "Payload must be an integer"}, status=400)

    # Map zones to tile numbers
    zone_to_tiles_map = {
        '0': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
        'a': [1, 2, 3, 4],
        'b': [6, 7, 8, 9],
        'c': [11, 12, 13, 14],
        'd': [1, 2, 3, 4, 5, 6, 7],
        'e': [8, 9, 10, 11, 12, 13, 14]
    }
    
    tile_numbers = zone_to_tiles_map.get(zone)
    if not tile_numbers:
        return JsonResponse({"error": f"Zone {zone} not recognized"}, status=400)

    # Get all devices for the zone
    devices = Device.objects.filter(
        arena=arena, 
        tile_label__in=[f"A{tile}" for tile in tile_numbers]
    )
    
    if not devices.exists():
        return JsonResponse({"error": f"No devices registered for zone {zone}"}, status=404)

    device_ids = [device.device_id for device in devices]

    def send_request(device_id):
        if device_id is None:
            return None
        try:
            url = f'https://info-beamer.com/api/v1/device/{device_id}/node/root/remote/trigger/'
            response = requests.post(url, data={"data": payload}, auth=('', api_key))
            return {"device_id": device_id, "trigger_status": response.status_code}
        except requests.RequestException as e:
            return {"device_id": device_id, "error": str(e)}

    start_time = time.time()
    print(f"🚀 Legacy: Triggering zone {zone} with {len(device_ids)} devices...")

    with ThreadPoolExecutor(max_workers=20) as executor:
        responses = list(executor.map(send_request, device_ids))

    responses = [r for r in responses if r is not None]
    duration_ms = (time.time() - start_time) * 1000
    print(f"✅ Legacy: Zone {zone} trigger completed in {duration_ms:.2f}ms")

    return JsonResponse({"results": responses, "duration_ms": duration_ms}, status=200)


@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def trigger_action(request):
    """Trigger an action on devices - For React frontend with JWT auth"""
    import time
    
    api_key = os.getenv("API_KEY")
    if not api_key:
        return JsonResponse({"error": "API key is missing"}, status=500)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    # For React frontend - arena_id in body
    arena_id = data.get("arena_id")
    zone = data.get("zone") or data.get("tile")
    payload = data.get("payload")
    setup_id = 257842

    if not arena_id or not zone or not payload:
        return JsonResponse({"error": "Missing arena_id, zone, or payload"}, status=400)
    
    # Check if user has control of the arena
    try:
        arena = Arena.objects.get(id=arena_id)
        if arena.active_controller != request.user:
            return JsonResponse({"error": "You are not the active controller"}, status=403)
    except Arena.DoesNotExist:
        return JsonResponse({"error": "Arena not found"}, status=404)

    try:
        payload_int = int(payload)
    except ValueError:
        return JsonResponse({"error": "Payload must be an integer"}, status=400)

    # Map zones to tile numbers (matches frontend)
    zone_to_tiles_map = {
        '0': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],  # All tiles
        'a': [1, 2, 3, 4],    # Tiles A1 to A4
        'b': [6, 7, 8, 9],    # Tiles A6 to A9
        'c': [11, 12, 13, 14], # Tiles A11 to A14
        'd': [1, 2, 3, 4, 5, 6, 7], # Tiles A1 to A7
        'e': [8, 9, 10, 11, 12, 13, 14] # Tiles A8 to A14
    }
    
    tile_numbers = zone_to_tiles_map.get(zone)
    if not tile_numbers:
        return JsonResponse({"error": f"Zone {zone} not recognized"}, status=400)

    # Get all devices for the zone (much more efficient than individual queries)
    devices = Device.objects.filter(
        arena=arena, 
        tile_label__in=[f"A{tile}" for tile in tile_numbers]
    )
    
    if not devices.exists():
        return JsonResponse({"error": f"No devices registered for zone {zone} in arena {arena.arena_name}"}, status=404)

    # Convert devices to list for indexing
    device_list = list(devices)
    device_ids = [device.device_id for device in device_list]

    # Payload mapping validation
    if payload_int >= 17 and str(payload_int) in payload_map:
        expected_payload_count = len(payload_map[str(payload_int)])
        if len(device_ids) != expected_payload_count:
            return JsonResponse({
                "error": f"Zone {zone} has {len(device_ids)} devices but payload {payload_int} requires {expected_payload_count} devices"
            }, status=400)

    def send_request(device_id, payload_value=None):
        """Optimized: Only send trigger, skip setup change for speed"""
        if device_id is None:
            return None
        try:
            # Only send trigger request (skip setup change for speed)
            url = f'https://info-beamer.com/api/v1/device/{device_id}/node/root/remote/trigger/'
            data_payload = {"data": payload_value or payload}
            response = requests.post(url, data=data_payload, auth=('', api_key))

            return {
                "device_id": device_id,
                "trigger_status": response.status_code
            }
        except requests.RequestException as e:
            return {"device_id": device_id, "error": str(e)}

    # Choose payload mapping
    if payload_int >= 17 and str(payload_int) in payload_map:
        payloads = payload_map[str(payload_int)]
    else:
        payloads = [payload] * len(device_ids)

    # Performance timing
    start_time = time.time()
    print(f"🚀 Triggering zone {zone} with {len(device_ids)} devices in parallel...")

    # Use ThreadPoolExecutor for maximum performance
    with ThreadPoolExecutor(max_workers=20) as executor:
        responses = list(executor.map(send_request, device_ids, payloads))

    # Filter out None responses
    responses = [response for response in responses if response is not None]
    
    end_time = time.time()
    duration_ms = (end_time - start_time) * 1000
    print(f"✅ Zone {zone} trigger completed in {duration_ms:.2f}ms")

    return JsonResponse({"results": responses, "duration_ms": duration_ms}, status=200)

@csrf_exempt
def switch_setup(request):
    arena_id = request.session.get('arena_id')
    if not arena_id:
        return JsonResponse({"error": "No arena in session"}, status=400)
    
    if request.method == "POST":
        api_key = os.getenv("API_KEY")
        setup_id = 257387
        payload = setup_id

        # Get all device IDs for this arena from database
        devices = Device.objects.filter(arena_id=arena_id)
        device_ids = [device.device_id for device in devices]
        
        if not device_ids:
            return JsonResponse({"error": "No devices registered for this arena"}, status=404)
            
        def send_request(device_id):
            if device_id is None:
                return None
            url = f'https://info-beamer.com/api/v1/device/{device_id}'
            response = requests.post(url, data={"setup_id": payload}, auth=('', api_key))
            return {"status": response.status_code}

        # Use ThreadPoolExecutor to send requests concurrently
        with ThreadPoolExecutor() as executor:
            responses = list(executor.map(send_request, device_ids))

        # Filter out None responses
        responses = [response for response in responses if response is not None]

        return JsonResponse({"results": responses}, status=200)
        
    return JsonResponse({"error": "Invalid request method"}, status=405)


def my_page(request):
    return render(request, 'dashboard/page_1.html')