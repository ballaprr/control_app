from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .views import fetch_legend_data  # Import the data-fetching function

def notify_legend_update():
    output_data = fetch_legend_data()
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "legend_updates",
        {
            "type": "send_update",
            "data": {"data": output_data},
        }
    )
