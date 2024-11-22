from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Pregunta
from django.http import JsonResponse

@login_required
def seccion2(request):
    preguntas = Pregunta.objects.filter(activo=True)
    return render(request, 'seccion2.html', {
        'preguntas': preguntas
    }) 