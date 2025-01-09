from django.shortcuts import render, redirect
from .models import Arena

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        arena_id = request.POST.get('arena')
        if arena_id:
            request.session['arena_id'] = arena_id
            return redirect('dashboard:dashboard')

    arenas = Arena.objects.all()
    print(arenas)
    return render(request, 'arena/login.html', {'arenas': arenas})