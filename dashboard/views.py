from django.shortcuts import render
from django.utils.timezone import now

def control_view(request):
    # Get current time in military format (HH:MM:SS)
    current_time = now().strftime("%H:%M:%S")  # Ensures military time format

    return render(request, 'dashboard/index.html', {
        'current_time': current_time,  # Pass the current time to the template
        'tile_range': range(1, 15)      # Send range from 1 to 14 for tiles
    })
