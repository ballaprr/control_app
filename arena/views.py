from django.shortcuts import render, redirect
from .models import Arena

def select_arena(request):
    if request.method == 'POST':
        arena_id = request.POST.get('arena_id')
        if arena_id:
            request.session['arena_id'] = arena_id
            return redirect('dashboard:dashboard')  # Redirect to the dashboard
    else:
        arenas = Arena.objects.all()
        print(arenas)
        return render(request, 'arena/select_arena.html', {'arenas': arenas})