from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import Arena

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        arena_id = request.POST.get('arena')
        print(arena_id)
        if arena_id:
            print(arena_id)
            request.session['arena_id'] = arena_id
            user = authenticate(request)  # Adjust for real logic
            if user:
                login(request, user)
                return redirect('dashboard:dashboard')
        else:
            pass

    arenas = Arena.objects.all()
    print(arenas)
    return render(request, 'arena/login.html', {'arenas': arenas})