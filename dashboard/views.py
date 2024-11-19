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
    "a": [39265, 39262, 39266, 39264],
    "b": None,
    "c": None,
    "d": [39265, 39262, 39266, 39264, None, None, None],
    "e": None,
    "0": [39265, 39262, 39266, 39264, None, None, None, None, None, None, None, None, None, None, None],
}

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



def control_view(request):
    # Get current time in military format (HH:MM:SS)
    current_time = now().strftime("%H:%M:%S")  # Ensures military time format

    return render(request, 'dashboard/index.html', {
        'current_time': current_time,  # Pass the current time to the template
        'tile_range': range(1, 15)      # Send range from 1 to 14 for tiles
    })

def device_output(request, title_Index):
    try:
        index = int(title_Index) - 1
        device_id = TILE_DEVICE_MAP.get("0")[index]
        if not device_id:
            return JsonResponse({"error": f"Device id does not exist"}, status=404)
          
        response = requests.get(f"https://info-beamer.com/api/v1/device/{device_id}/output", auth=('', os.getenv("API_KEY")))
        print(response)
        if response.status_code == 200:
           return JsonResponse(response.json(), status=200)
        else:
            return JsonResponse({"error": f"Failed to get output for device {device_id}"}, status=500)
            
    except (ValueError, IndexError):
        return JsonResponse({"error": "Invalid index"}, status=400)


@csrf_exempt
def blackscreen(request):
    if request.method == "POST":
        api_key = os.getenv("API_KEY")
        device_ids = TILE_DEVICE_MAP.get("0")

        def send_request(device_id):
            url = f'https://info-beamer.com/api/v1/device/{device_id}/node/root/remote/trigger/'
            response = requests.post(url, data={"data": "1000"}, auth=('', api_key))
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
        if response.status_code == 200:
           return JsonResponse(response.json(), status=200)
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
        print(payload_int)
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