from django.urls import path
from . import views

app_name = 'arena'

urlpatterns = [
    path('select-arena/', views.select_arena, name='select_arena'),
]
