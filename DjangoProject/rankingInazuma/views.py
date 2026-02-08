import csv
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone

# Tus modelos específicos
from .forms import RegisterForm, LoginForm
from .models import Elemento, Categoria, Ranking, Reviews


def go_home(request):
    return render(request, 'inicio.html')

def do_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, nombre=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('go_home')
            else:
                messages.error(request, "Acceso denegado. Revisa tus datos.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {"form": form})


def do_register(request):
    if request.method == 'POST':
        dataform = RegisterForm(request.POST)
        if dataform.is_valid():
            user = dataform.save(commit=False)
            user.set_password(dataform.cleaned_data['password'])
            user.save()
            messages.success(request, "¡Fichaje completado! Ya puedes entrar al equipo.")
            return redirect('do_login')
        else:
            return render(request, 'register.html', {"form": dataform})
    else:
        form = RegisterForm()
        return render(request, 'register.html', {"form": form})

def logout_user(request):
    logout(request)
    return redirect('go_home')


def es_admin(user):
    return user.is_authenticated and user.rol == 'admin'


@user_passes_test(es_admin)
def go_admin_panel(request):
    return render(request, 'admin.html')


@user_passes_test(es_admin)
def data_load(request):
    """Carga masiva con lógica de actualización (RF10)"""
    if request.method == "POST":
        archivo_csv = request.FILES.get('csvFile')
        if not archivo_csv:
            messages.error(request, 'Debes seleccionar un archivo CSV de la Temporada 1.')
            return redirect('data_load')

        # Leemos el archivo
        lineas = archivo_csv.read().decode('utf-8').splitlines()
        lector = csv.DictReader(lineas)

        contador_nuevos = 0
        contador_actualizados = 0

        for fila in lector:
            nombre_item = fila['Nombre']

            # Buscamos si el personaje/equipo ya existe en la base de datos
            # Usamos .filter().first() para que no de error si no encuentra nada
            existente = Elemento.objects.filter(nombre=nombre_item).first()

            if existente:
                # 1. SI EXISTE: Actualizamos sus datos (por si ha cambiado la imagen o la posición)
                existente.posicion = fila.get('Posicion', 'Sin definir')
                existente.imageUrl = fila['Imagen']
                existente.save()
                contador_actualizados += 1
            else:
                # 2. NO EXISTE: Creamos un nuevo registro
                nuevo = Elemento()
                nuevo.nombre = nombre_item
                nuevo.posicion = fila.get('Posicion', 'Sin definir')
                nuevo.imageUrl = fila['Imagen']

                # Generamos el código autoincremental para MongoDB
                ultimo = Elemento.objects.order_by('code').last()
                nuevo.code = (ultimo.code + 1) if ultimo else 1

                nuevo.save()
                contador_nuevos += 1

        messages.success(request,
                         f"¡Proceso completado! Fichados: {contador_nuevos}. Actualizados: {contador_actualizados}.")
        return redirect('go_admin_panel')

    return render(request, 'data_load.html')


@user_passes_test(es_admin)
def categories(request):
    categorias_lista = Categoria.objects.all()
    elementos_disponibles = Elemento.objects.all()

    if request.method == "POST":
        nueva_categoria = Categoria()
        # CORRECCIÓN: 'name' debe coincidir con el name del input en el HTML
        nueva_categoria.name = request.POST.get('name')
        nueva_categoria.logo = request.POST.get('logo')
        nueva_categoria.description = request.POST.get('description')

        ultima_categoria = Categoria.objects.order_by('code').last()
        nueva_categoria.code = (ultima_categoria.code + 1) if ultima_categoria else 1

        seleccion_json = request.POST.get('items_seleccionados')
        nueva_categoria.listaElementos = [int(x) for x in json.loads(seleccion_json)]

        nueva_categoria.save()
        messages.success(request, "Nueva categoría Inazuma creada correctamente.")
        return redirect('categories')

    return render(request, 'categorias.html', {
        'categorias': categorias_lista,
        'elementos': elementos_disponibles
    })


@user_passes_test(es_admin)
def delete_category(request, code):
    Categoria.objects.filter(code=code).delete()
    messages.warning(request, "Categoría eliminada.")
    return redirect('categories')



def show_categories(request):
    categorias = Categoria.objects.all()
    return render(request, 'ranking_categorias.html', {'categorias': categorias})

def go_rankings(request, id):
    try:
        categoria = Categoria.objects.get(code=id)
        items_para_rankear = Elemento.objects.filter(code__in=categoria.listaElementos)
    except Categoria.DoesNotExist:
        messages.error(request, "No se encuentra esa sección.")
        return redirect('show_categories')

    return render(request, 'ranking.html', {
        'items': items_para_rankear,
        'categoria_code': categoria.code,
        'titulo': categoria.nombre
    })


@login_required
def rankings_usuario(request):
    # Usamos 'usuario' y 'fecha_creacion' que son los campos de tu modelo
    mis_tops = Ranking.objects.filter(usuario=request.user.nombre).order_by('-fecha_creacion')
    return render(request, 'rankings_usuario.html', {'rankings': mis_tops})

@login_required
def save_top(request):
    if request.method == 'POST':
        order_json = request.POST.get('order')
        categoria_code = request.POST.get('categoria_code')

        try:
            ids_ordenados = [int(i['id']) for i in json.loads(order_json)]

            ranking = Ranking()

            ranking.fecha_creacion = timezone.now()
            ranking.usuario = request.user.nombre
            ranking.categoriaCode = int(categoria_code)
            ranking.rankinLista = ids_ordenados
            ranking.save()

            messages.success(request, "¡Tu Ranking ha sido guardado con éxito!")
        except Exception as e:
            print(f"Error: {e}") # Para debug en consola
            messages.error(request, "Error al guardar el ranking.")

    return redirect('go_home')


def guardar_review(request):
    if request.method == "POST":
        elemento_code = int(request.POST.get('elementoCode'))
        puntuacion = int(request.POST.get('puntuacion'))
        comentario = request.POST.get('comentario')
        nombre_usuario = request.user.nombre


        review, created = Reviews.objects.update_or_create(
            usuario=nombre_usuario,
            elementoCode=elemento_code,
            defaults={
                'puntuacion': puntuacion,
                'comentario': comentario,
                'fecha': timezone.now()
            }
        )

        if created:
            messages.success(request, "¡Fichaje valorado con éxito!")
        else:
            messages.info(request, "Valoración actualizada correctamente.")

    return redirect('mostrar_elementos')


def mostrar_elementos(request):
    elementos = Elemento.objects.all()

    puntuaciones_dict = {}
    if request.user.is_authenticated:
        user_reviews = Reviews.objects.filter(usuario=request.user.nombre)
        for r in user_reviews:
            puntuaciones_dict[r.elementoCode] = {
                'puntuacion': r.puntuacion,
                'comentario': r.comentario
            }

    for elemento in elementos:
        review_data = puntuaciones_dict.get(elemento.code)
        if review_data:
            elemento.nota_actual = review_data['puntuacion']
            elemento.comentario_actual = review_data['comentario']
        else:
            elemento.nota_actual = None

    return render(request, 'elementos.html', {'elementos': elementos})