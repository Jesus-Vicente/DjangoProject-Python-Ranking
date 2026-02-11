import csv
import json

from django.db.models.aggregates import Avg, Count
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone

from .forms import RegisterForm, LoginForm
from .models import Elemento, Categoria, Ranking, Reviews


# --- VISTAS DE ACCESO ---

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


# --- PANEL ADMIN Y CARGA DE DATOS ---

def es_admin(user):
    return user.is_authenticated and user.rol == 'admin'


@user_passes_test(es_admin)
def go_admin_panel(request):
    return render(request, 'admin.html')


@user_passes_test(es_admin)
def data_load(request):
    """Carga masiva con lógica de actualización (RF10) + Afinidad"""
    if request.method == "POST":
        archivo_csv = request.FILES.get('csvFile')
        if not archivo_csv:
            messages.error(request, 'Debes seleccionar un archivo CSV.')
            return redirect('data_load')

        lineas = archivo_csv.read().decode('utf-8').splitlines()
        lector = csv.DictReader(lineas)

        contador_nuevos = 0
        contador_actualizados = 0

        for fila in lector:
            nombre_item = fila['Nombre']
            existente = Elemento.objects.filter(nombre=nombre_item).first()

            if existente:
                existente.posicion = fila.get('Posicion', 'Sin definir')
                existente.afinidad = fila.get('Afinidad', 'Neutral')
                existente.imageUrl = fila['Imagen']
                existente.save()
                contador_actualizados += 1
            else:
                nuevo = Elemento()
                nuevo.nombre = nombre_item
                nuevo.posicion = fila.get('Posicion', 'Sin definir')
                nuevo.afinidad = fila.get('Afinidad', 'Neutral')
                nuevo.imageUrl = fila['Imagen']
                nuevo.categoriaCode = int(fila.get('CategoriaCode', 1))  # Importante para que aparezcan en ranking
                nuevo.temporadaCode = 1
                nuevo.descripcion = fila.get('Descripcion', 'Jugador de la Temporada 1')

                ultimo = Elemento.objects.order_by('code').last()
                nuevo.code = (ultimo.code + 1) if ultimo else 1
                nuevo.save()
                contador_nuevos += 1

        messages.success(request,
                         f"Proceso completado! Nuevos: {contador_nuevos}. Actualizados: {contador_actualizados}.")
        return redirect('go_admin_panel')
    return render(request, 'data_load.html')


@user_passes_test(es_admin)
def categories(request):
    categorias_lista = Categoria.objects.all()
    elementos_disponibles = Elemento.objects.all()

    if request.method == "POST":
        nueva_categoria = Categoria()
        nueva_categoria.nombre = request.POST.get('nombre')

        logo_url = request.POST.get('logo')
        nueva_categoria.logo = logo_url if logo_url else "/static/images/default.png"
        nueva_categoria.descripcion = request.POST.get('description')

        ultima_categoria = Categoria.objects.order_by('code').last()
        nueva_categoria.code = (ultima_categoria.code + 1) if ultima_categoria else 1

        seleccion_json = request.POST.get('items_seleccionados')
        nueva_categoria.listaElementos = [int(x) for x in json.loads(seleccion_json)] if seleccion_json else []

        nueva_categoria.save()
        messages.success(request, "Nueva categoría creada.")
        return redirect('categories')

    return render(request, 'categorias.html', {'categorias': categorias_lista, 'elementos': elementos_disponibles})


@user_passes_test(es_admin)
def delete_category(request, code):
    Categoria.objects.filter(code=code).delete()
    messages.warning(request, "Categoría eliminada.")
    return redirect('categories')


# --- RANKINGS Y EXPLORACIÓN ---

def show_categories(request):
    categorias = Categoria.objects.all()
    return render(request, 'ranking_categorias.html', {'categorias': categorias})


def go_rankings(request, id):
    try:
        categoria_obj = Categoria.objects.get(code=id)
        # Intentamos filtrar de dos formas para asegurar
        elementos_para_rankear = Elemento.objects.filter(categoriaCode=int(id))

        if not elementos_para_rankear.exists():
            # Si lo anterior falla, intentamos por la lista de IDs guardada en la categoría
            elementos_para_rankear = Elemento.objects.filter(code__in=categoria_obj.listaElementos)

        # DEBUG: Mira tu consola de Python al cargar la página
        print(f"DEBUG: Categoria {id} - Elementos encontrados: {elementos_para_rankear.count()}")

    except Categoria.DoesNotExist:
        messages.error(request, "Categoría no encontrada.")
        return redirect('show_categories')

    return render(request, 'ranking.html', {
        'elementos': elementos_para_rankear,
        'categoria': categoria_obj,
        'ids_en_top': [],
        'edit_mode': False
    })

@login_required
def save_top(request):
    if request.method == 'POST':
        rankin_lista_json = request.POST.get('rankinLista')
        categoria_code = request.POST.get('categoriaCode')
        ranking_id = request.POST.get('rankingId')

        try:
            lista_original = json.loads(rankin_lista_json)
            lista_enriquecida = []

            for item in lista_original:
                jugador = Elemento.objects.filter(code=item['elementoCode']).first()
                if jugador:
                    # Guardamos la posición explícitamente como string para el selector de JS
                    lista_enriquecida.append({
                        "posicion": str(item['posicion']),
                        "pos": jugador.posicion,
                        "nombre": jugador.nombre,
                        "img": jugador.imageUrl,
                        "elementoCode": item['elementoCode']
                    })

            if ranking_id and ranking_id != "":
                Ranking.objects.filter(id=ranking_id, usuario=request.user.nombre).update(
                    rankinLista=lista_enriquecida,
                    fecha_creacion=timezone.now()
                )
                messages.success(request, "Estrategia actualizada.")
            else:
                nuevo_ranking = Ranking(
                    usuario=request.user.nombre,
                    categoriaCode=int(categoria_code),
                    rankinLista=lista_enriquecida,
                    fecha_creacion=timezone.now()
                )
                nuevo_ranking.save()
                messages.success(request, "Ranking guardado.")

        except Exception as e:
            messages.error(request, f"Error: {e}")

    return redirect('rankings_usuario')

@login_required
def ranking_usuario(request):
    mis_tops = Ranking.objects.filter(usuario=request.user.nombre).order_by('-fecha_creacion')
    categorias = {c.code: c.nombre for c in Categoria.objects.all()}
    for r in mis_tops:
        r.nombre_categoria = categorias.get(r.categoriaCode, "Desconocida")
    return render(request, 'rankings_usuario.html', {'rankings': mis_tops})


@login_required
def editar_ranking(request, ranking_id):
    """Carga un ranking existente para editarlo"""
    ranking_existente = get_object_or_404(Ranking, id=ranking_id, usuario=request.user.nombre)
    categoria_obj = get_object_or_404(Categoria, code=ranking_existente.categoriaCode)

    # Misma lógica de búsqueda de elementos que en go_rankings
    elementos_para_rankear = Elemento.objects.filter(categoriaCode=ranking_existente.categoriaCode)
    if not elementos_para_rankear.exists():
        elementos_para_rankear = Elemento.objects.filter(code__in=categoria_obj.listaElementos)

    # Convertimos los IDs a strings para que el template los compare correctamente
    ids_en_top = [str(item['elementoCode']) for item in ranking_existente.rankinLista]

    return render(request, 'ranking.html', {
        'elementos': elementos_para_rankear,
        'categoria': categoria_obj,
        'ranking_editando': ranking_existente,
        'ids_en_top': ids_en_top,
        'edit_mode': True
    })


@login_required
def eliminar_mi_ranking(request, ranking_id):
    # Usar .nombre porque es el campo que defines en tu modelo de Usuario/Ranking
    ranking_a_eliminar = Ranking.objects.filter(id=ranking_id, usuario=request.user.nombre)

    if ranking_a_eliminar.exists():
        ranking_a_eliminar.delete()
        messages.warning(request, "Alineación eliminada.")
    else:
        messages.error(request, "No se pudo eliminar el ranking.")

    return redirect('rankings_usuario')

# --- REVIEWS Y ELEMENTOS ---

@login_required
def guardar_review(request):
    if request.method == "POST":
        try:
            elemento_code = int(request.POST.get('elementoCode'))
            puntuacion = int(request.POST.get('puntuacion')) # Ahora viene de las estrellas
            comentario = request.POST.get('comentario')

            Reviews.objects.update_or_create(
                usuario=request.user.nombre,
                elementoCode=elemento_code,
                defaults={
                    'puntuacion': puntuacion,
                    'comentario': comentario,
                    'fecha': timezone.now()
                }
            )
            messages.success(request, "¡Valoración guardada!")
        except Exception as e:
            messages.error(request, f"Error al guardar: {e}")
    return redirect('mostrar_elementos')


def estadisticas_view(request):
    # 1. Total de todas las reviews en el sistema
    total_valoraciones = Reviews.objects.count()

    # 2. Ranking de Élite: Elementos con más valoraciones
    # Obtenemos los elementos y les pegamos los datos de las reviews
    todos_elementos = Elemento.objects.all()
    mas_valorados = []

    for el in todos_elementos:
        # Filtramos reviews para este elemento usando su 'code'
        votos_el = Reviews.objects.filter(elementoCode=el.code)
        conteo = votos_el.count()

        if conteo > 0:
            promedio = votos_el.aggregate(Avg('puntuacion'))['puntuacion__avg']
            mas_valorados.append({
                'nombre': el.nombre,
                'imagen_url': el.imageUrl,
                'posicion_campo': el.posicion,
                'afinidad': el.afinidad,
                'conteo': conteo,
                'promedio': round(promedio, 1),
                'id': el.code
            })

    # Ordenamos por conteo de votos (descendente) y tomamos el TOP 10
    mas_valorados = sorted(mas_valorados, key=lambda x: x['conteo'], reverse=True)[:10]

    # 3. Distribución por Categoría
    categorias_lista = Categoria.objects.all()
    promedios = []

    for cat in categorias_lista:
        # Contamos cuántas reviews pertenecen a elementos de esta categoría
        votos_categoria = Reviews.objects.filter(
            elementoCode__in=Elemento.objects.filter(categoriaCode=cat.code).values_list('code', flat=True)
        ).count()

        porcentaje = (votos_categoria / total_valoraciones * 100) if total_valoraciones > 0 else 0

        promedios.append({
            'nombre': cat.nombre,
            'porcentaje': round(porcentaje, 1)
        })

    context = {
        'total_valoraciones': total_valoraciones,
        'mas_valorados': mas_valorados,
        'promedios': promedios,
    }

    return render(request, 'estadisticas.html', context)


def get_valoraciones_detalles(request, elemento_id):
    """Devuelve las valoraciones de un personaje en formato JSON"""
    # Filtramos por elementoCode
    valoraciones_qs = Reviews.objects.filter(elementoCode=elemento_id).order_by('-fecha')

    data = []
    for v in valoraciones_qs:
        data.append({
            # Si el usuario es nulo por alguna razón, ponemos "Anónimo"
            'usuario': v.usuario if v.usuario else "ANÓNIMO",
            'puntuacion': v.puntuacion,
            'comentario': v.comentario,
            'fecha': v.fecha.strftime('%d/%m/%Y %H:%M')
        })

    return JsonResponse({'valoraciones': data})


def personaje_detalle(request, elemento_id):
    # 1. Buscamos el personaje usando el campo 'code' de tu modelo Elemento
    personaje = get_object_or_404(Elemento, code=elemento_id)

    # 2. Obtenemos todas las reviews asociadas a ese elementoCode
    valoraciones = Reviews.objects.filter(elementoCode=elemento_id).order_by('-fecha')

    # 3. Calculamos el promedio de puntuación
    promedio_data = valoraciones.aggregate(Avg('puntuacion'))
    promedio = promedio_data['puntuacion__avg'] if promedio_data['puntuacion__avg'] else 0

    return render(request, 'detalles_personaje.html', {
        'personaje': personaje,
        'valoraciones': valoraciones,
        'promedio': round(promedio, 1)
    })

def mostrar_elementos(request):
    query = request.GET.get('q')
    elementos = Elemento.objects.filter(nombre__icontains=query) if query else Elemento.objects.all()

    puntuaciones_dict = {}
    if request.user.is_authenticated:
        user_reviews = Reviews.objects.filter(usuario=request.user.nombre)
        for r in user_reviews:
            puntuaciones_dict[r.elementoCode] = {'puntuacion': r.puntuacion, 'comentario': r.comentario}

    for el in elementos:
        review = puntuaciones_dict.get(el.code)
        el.nota_actual = review['puntuacion'] if review else None
        el.comentario_actual = review['comentario'] if review else ""

    return render(request, 'elementos.html', {'elementos': elementos, 'query': query})