from django.shortcuts import render
from django.utils.timezone import now
from django.http import JsonResponse
import requests
import json
import os
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

load_dotenv()


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
        # Forward the request to the external API
        url = 'https://info-beamer.com/api/v1/device/39265/node/root/remote/trigger/'
        payload = {'data': 'a'}
        try:
            response = requests.post(url, data=payload, auth=('', api_key))
            if response.status_code == 200 and response.json().get("ok") == True:
                return JsonResponse({'ok': True, 'message': 'Action triggered successfully.'})
            else:
                return JsonResponse({'ok': False, 'message': 'Failed to trigger action.'})
        except requests.RequestException as e:
            return JsonResponse({"error": str(e)}, status=500)
        
    return JsonResponse({'ok': False, 'message': 'Invalid request method.'})