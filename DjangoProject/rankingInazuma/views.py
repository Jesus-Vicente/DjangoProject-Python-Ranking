from django.shortcuts import render

from rankingInazuma.models import Character


# Create your views here.

def go_home(request):
    return render(request, 'inicio.html')

def show_characters(request):

    lista_personajes = Character.objects.all()

    return render(request, 'personajes.html'), {'lista': lista_personajes}
