import os
import json
import django

# 1. Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProjectClase.settings')
django.setup()

from rankingInazuma.models import Elemento, Categoria, Temporada


def importar_inazuma():
    # Ruta al archivo JSON
    json_path = 'personajes_nosql.json'

    if not os.path.exists(json_path):
        print(f"Error: No se encuentra el archivo {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        datos = json.load(f)

    print(f"Iniciando importación de {len(datos)} elementos...")

    # Creamos una categoría y temporada por defecto si no existen
    # (Para que los foreign keys/codes tengan sentido)
    cat, _ = Categoria.objects.using('mongodb').get_or_create(
        code=1, defaults={'nombre': 'Jugadores', 'descripcion': 'Todos los jugadores'}
    )
    temp, _ = Temporada.objects.using('mongodb').get_or_create(
        code=1, defaults={'nombre': 'Temporada 1', 'descripcion': 'Saga original'}
    )

    for i, item in enumerate(datos, start=1):
        # Limpieza simple de afinidad y posicion
        afinidad = item.get('afinidad', 'N/A')
        posicion = item.get('posicion', 'N/A')

        # Crear el elemento en MongoDB
        Elemento.objects.using('mongodb').create(
            code=i,
            nombre=item['nombre'],
            descripcion=f"Jugador con afinidad {afinidad}",
            categoriaCode=cat.code,
            temporadaCode=temp.code,
            posicion=posicion,
            afinidad=afinidad,
            equipos=item.get('equipo', []),
            imageUrl=item.get('url_imagen', '')
        )

        if i % 50 == 0:
            print(f"Procesados {i} jugadores...")

    print("¡Importación completada con éxito!")


if __name__ == '__main__':
    importar_inazuma()