import csv

import requests
import json
from bs4 import BeautifulSoup
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render, redirect

from .forms import RegisterForm, LoginForm
from .models import Elemento, Categoria, Ranking


def do_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('go_home')
    else:
        form = LoginForm()

    return render(request, 'login.html', {"form": form})


def do_register(request):
    if request.method == 'POST':
        dataform = RegisterForm(request.POST)

        # validaciones
        if dataform.is_valid():
            user = dataform.save(commit=False)
            user.set_password(dataform.cleaned_data['password'])
            user.save()
            return redirect('do_login')
        else:
            return render(request, 'register.html', {"form": dataform})
    else:
        form = RegisterForm()
        return render(request, 'register.html', {"form": form})


def logout_user(request):
    logout(request)
    return render(request, 'inicio.html')

def do_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('go_home')
    else:
        form = LoginForm()

    return render(request, 'login.html', {"form": form})


def do_register(request):
    if request.method == 'POST':
        dataform = RegisterForm(request.POST)

        # validaciones
        if dataform.is_valid():
            user = dataform.save(commit=False)
            user.set_password(dataform.cleaned_data['password'])
            user.save()
            return redirect('do_login')
        else:
            return render(request, 'register.html', {"form": dataform})
    else:
        form = RegisterForm()
        return render(request, 'register.html', {"form": form})


def logout_user(request):
    logout(request)
    return render(request, 'inicio.html')


def go_home(request):
    return render(request, 'inicio.html')


def show_categories(request):
    # Usamos tu campo 'nombre' y 'descripcion'
    categories = Categoria.objects.all()
    return render(request, 'categorias.html', {'categorias': categories})


def mostrar_elementos(request):
    elementos = Elemento.objects.all()
    return render(request, 'elementos.html', {'elementos': elementos})


def go_rankings(request, id):
    category = Categoria.objects.get(code=id)
    # Filtramos Elementos usando tu campo 'code' y 'listaElementos' de Categoria
    list_elementos = Elemento.objects.filter(code__in=category.listaElementos)
    return render(request, 'ranking.html', {
        'items': list_elementos,
        'category_code': category.code,
        'category_size': len(category.listaElementos),
    })


def data_load(request):
    if request.method == "POST":
        action = request.POST.get('action')

        # OPCIÓN 1: Tu Web Scraping
        if action == "scraping":
            url = "https://inazuma.fandom.com/es/wiki/Categoría:Personajes_(IE_Original_T1)"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            personajes = soup.find_all('a', class_='category-page__member-link')

            for i, p in enumerate(personajes):
                nombre = p.text.strip()
                if "Categoría" not in nombre:
                    Elemento.objects.update_or_create(
                        nombre=nombre,
                        defaults={
                            'code': i + 1,
                            'descripcion': 'Cargado vía Scraping',
                            'categoriaCode': 1,
                            'temporadaCode': 1
                        }
                    )
            return redirect('go_home')

        # OPCIÓN 2: El CSV del Profesor
        elif action == "csv":
            uploaded_file = request.FILES.get('csvFile')
            if uploaded_file:
                decoded_file = uploaded_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                for i, row in enumerate(reader):
                    Elemento.objects.update_or_create(
                        nombre=row['Nombre'],  # Asegúrate que tu CSV tenga esta cabecera
                        defaults={
                            'code': 1000 + i,
                            'descripcion': row.get('Descripcion', 'Sin descripción'),
                            'categoriaCode': 1,
                            'temporadaCode': 1
                        }
                    )
            return redirect('go_home')

    return render(request, 'data_load.html')


