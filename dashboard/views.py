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



def control_view(request):
    # Get current time in military format (HH:MM:SS)
    current_time = now().strftime("%H:%M:%S")  # Ensures military time format

    return render(request, 'dashboard/index.html', {
        'current_time': current_time,  # Pass the current time to the template
        'tile_range': range(1, 15)      # Send range from 1 to 14 for tiles
    })


@csrf_exempt
def trigger_action(request):
    if request.method == "POST":
        api_key = os.getenv("API_KEY")
        tile = "a"
        payload = "2"
        # Forward the request to the external API
        if not tile or not payload:
                return JsonResponse({"error": "Missing tile or payload"}, status=400)
        
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

        # Filter out None responses
        responses = [response for response in responses if response is not None]
        #

        return JsonResponse({"results": responses}, status=200)
        
    return JsonResponse({"error": "Invalid request method"}, status=405)