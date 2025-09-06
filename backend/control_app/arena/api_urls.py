from django.urls import path
from . import api_views

app_name = 'arena_api'

urlpatterns = [
    # Arena CRUD endpoints
    path('', api_views.ArenaListCreateView.as_view(), name='arena-list-create'),
    path('<int:pk>/', api_views.ArenaDetailView.as_view(), name='arena-detail'),
    
    # Arena control endpoints
    path('<int:arena_id>/take-control/', api_views.take_control, name='take-control'),
    path('<int:arena_id>/release-control/', api_views.release_control, name='release-control'),
    path('<int:arena_id>/brightness/', api_views.update_brightness, name='update-brightness'),
]
