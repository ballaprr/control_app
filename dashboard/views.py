from django.shortcuts import render
from django.utils.timezone import now
from django.http import JsonResponse
import requests
import json
import os
from django.views.decorators.csrf import csrf_exempt
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()


TILE_DEVICE_MAP = {
    "a": [39353, 39354, None, None],
    "b": [39265, 39262, 39266, 39264], 
    "c": [None, None, None, None],
    "d": [None, None, None, None, 39265, 39262],
    "e": [39266, 39264, None, None, None, None],
    "0": [39353, 39354, None, None, 39265, 39262, 39266, 39264, None, None, None, None]
}
"""

TILE_DEVICE_MAP = {
    "a": [39353, 39354, 39357, 39358],
    "b": [39268, 39269, 39270, 39271],
    "c": [39272, 39274, 39277, 39278],
    "d": [39353, 39354, 39357, 39358, 39268, 39269],
    "e": [39270, 39271, 39272, 39274, 39277, 39278],
    "0": [39353, 39354, 39357, 39358, 39268, 39269, 39270, 39271, 39272, 39274, 39277, 39278],
}
"""

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
            ids = [item.get("id") for item in setups['setups']]
            return ids
        else:
            return JsonResponse({"error": "Failed to get setups"}, status=500)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": "Failed to get setups"}, status=500)

# function is called when page is reloaded
def control_view(request):
    # Get current time in military format (HH:MM:SS)
    triggers_to_replace = ['59', '60', '61', '62']
    current_time = now().strftime("%H:%M:%S")  # Ensures military time format
    output_data = fetch_legend_data(request, 254745)
    ids = get_setups(request)
    return render(request, 'dashboard/index.html', {
        'output_data': output_data,       # Pass the output data to the template
        'current_time': current_time,  # Pass the current time to the template
        'tile_range': range(1, 13),      # Send range from 1 to 14 for tiles
        'triggers_to_replace': triggers_to_replace,
        'ids': ids,
    })

def fetch_legend_data_api(request, setup_id):
    output_data = fetch_legend_data(request, setup_id)
    return JsonResponse(output_data, safe=False)

def device_output(request, title_Index):
    try:
        index = int(title_Index) - 1
        device_id = TILE_DEVICE_MAP.get("0")[index]
        if not device_id:
            return JsonResponse({"error": f"Device id does not exist"}, status=404)
          
        response = requests.get(f"https://info-beamer.com/api/v1/device/{device_id}/output", auth=('', os.getenv("API_KEY")))
        if response.status_code == 200:
           return JsonResponse(response.json(), status=200)
        else:
            return JsonResponse({"error": f"Failed to get output for device {device_id}"}, status=500)
            
    except (ValueError, IndexError):
        return JsonResponse({"error": "Invalid index"}, status=400)

@csrf_exempt
def reboot_device(request):
    if request.method == "POST":
        api_key = os.getenv("API_KEY")
        data = json.loads(request.body)
        index = data.get("tile")
        device_id = TILE_DEVICE_MAP.get("0")[int(index) - 1]
        if not device_id:
            return JsonResponse({"error": f"Device id does not exist"}, status=404)
        
        response = requests.post(f"https://info-beamer.com/api/v1/device/{device_id}/reboot", auth=('', api_key))
        if response.status_code == 200:
            return JsonResponse({"status": "Device rebooted successfully"}, status=200)
        else:
            return JsonResponse({"error": "Failed to reboot device"}, status=500)

@csrf_exempt
def blackscreen(request):
    if request.method == "POST":
        api_key = os.getenv("API_KEY")
        device_ids = TILE_DEVICE_MAP.get("0")

        def send_request(device_id):
            url = f'https://info-beamer.com/api/v1/device/{device_id}/node/root/remote/trigger/'
            response = requests.post(url, data={"data": "m"}, auth=('', api_key))
            return {"device_id": device_id, "status": response.status_code}
        
        with ThreadPoolExecutor() as executor:
                responses = list(executor.map(send_request, device_ids))

        responses = [response for response in responses if response is not None]

        return JsonResponse({"results": responses}, status=200)
          
@csrf_exempt
def get_deviceid(request, tileIndex):
    try:
        api_key = os.getenv("API_KEY")
        tileIndex = int(tileIndex) - 1
        device_id = TILE_DEVICE_MAP.get("0")[tileIndex]
        if not device_id:
            return JsonResponse({"error": f"Device id does not exist"}, status=404)
        
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
def trigger_action(request):
    if request.method == "POST":
        api_key = os.getenv("API_KEY")
        data = json.loads(request.body)
        tile = data.get("tile")
        payload = data.get("payload")
        # Forward the request to the external API
        if not tile or not payload:
                return JsonResponse({"error": "Missing tile or payload"}, status=400)
        
        payload_int = int(payload)
        if payload_int < 17:
            device_ids = TILE_DEVICE_MAP.get(tile)
            if device_ids is None:
                    return JsonResponse({"error": f"Tile {tile} not recognized"}, status=404)
            
            # 
            def send_request(device_id):
                if device_id is None:
                    return None
                url = f'https://info-beamer.com/api/v1/device/{device_id}/node/root/remote/trigger/'
                response = requests.post(url, data={"data": payload}, auth=('', api_key))
                return {"device_id": device_id, "status": response.status_code}

            # Use ThreadPoolExecutor to send requests concurrently
            with ThreadPoolExecutor() as executor:
                responses = list(executor.map(send_request, device_ids))

        else:
            device_ids = TILE_DEVICE_MAP.get(tile)
            if device_ids is None:
                    return JsonResponse({"error": f"Tile {tile} not recognized"}, status=404)
            
            if len(device_ids) != len(payload_map[payload]):
                return JsonResponse({"error": f"Tile {tile} does not have the correct number of devices"}, status=400)
            
            def send_request(device_id, payload):
                if device_id is None:
                    return None
                url = f'https://info-beamer.com/api/v1/device/{device_id}/node/root/remote/trigger/'
                response = requests.post(url, data={"data": payload}, auth=('', api_key))
                return {"device_id": device_id, "status": response.status_code}

            # Use ThreadPoolExecutor to send requests concurrently
            with ThreadPoolExecutor() as executor:
                responses = list(executor.map(send_request, device_ids, payload_map[payload]))

        # Filter out None responses
        responses = [response for response in responses if response is not None]
        #

        return JsonResponse({"results": responses}, status=200)
        
    return JsonResponse({"error": "Invalid request method"}, status=405)