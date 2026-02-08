import cloudscraper
from bs4 import BeautifulSoup
import csv
import time
import random


def extraer_imagen_jugador(url, scraper):
    try:
        time.sleep(random.uniform(2.0, 4.0))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
        }

        res = scraper.get(url, headers=headers, timeout=15)
        if res.status_code != 200: return None

        soup = BeautifulSoup(res.text, 'html.parser')

        nombre_tag = soup.find('h1', id='firstHeading')
        nombre = nombre_tag.text.strip() if nombre_tag else "Desconocido"

        # Buscamos la imagen principal en la infobox
        img_tag = soup.select_one('aside.portable-infobox img.pi-image-thumbnail')

        url_imagen = "N/A"
        if img_tag:
            # Capturamos la URL completa.
            # Intentamos primero 'src' que suele traer la versión renderizada final,
            # y si no 'data-src'. No hacemos split para no romper el enlace.
            url_imagen = img_tag.get('src') or img_tag.get('data-src')

            # Si la URL empieza por "data:image", es un placeholder, buscamos data-src
            if url_imagen and url_imagen.startswith('data:image'):
                url_imagen = img_tag.get('data-src')

        return {'nombre': nombre, 'url_imagen': url_imagen}
    except Exception:
        return None


def ejecutar():
    scraper = cloudscraper.create_scraper(
        browser={
            'custom': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'}
    )

    url_actual = "https://inazuma.fandom.com/es/wiki/Categor%C3%ADa:Personajes_(IE_Original_T1)"
    urls_totales = []

    print("--- 🔍 Escaneando todas las páginas de la categoría ---")
    while url_actual:
        try:
            res_cat = scraper.get(url_actual)
            soup_cat = BeautifulSoup(res_cat.text, 'html.parser')
            enlaces = ["https://inazuma.fandom.com" + a['href'] for a in soup_cat.select('.category-page__member-link')]
            urls_totales.extend(enlaces)
            print(f"✅ {len(enlaces)} personajes encontrados en esta página...")

            boton_siguiente = soup_cat.select_one('a.category-page__pagination-next')
            url_actual = boton_siguiente['href'] if boton_siguiente else None
        except:
            break

    print(f"\n--- 🖼️ Extrayendo URLs completas ({len(urls_totales)} personajes) ---")

    resultados = []
    for i, url in enumerate(urls_totales):
        info = extraer_imagen_jugador(url, scraper)
        if info:
            # Imprimimos un trozo de la URL para verificar que lleva el /revision/
            print(f"[{i + 1}/{len(urls_totales)}] {info['nombre']} -> URL detectada correctamente")
            resultados.append(info)

        if (i + 1) % 10 == 0:
            guardar_csv_imagenes(resultados)

    guardar_csv_imagenes(resultados)
    print("\n✅ Proceso completado. Revisa 'jugadores_imagenes.csv'")


def guardar_csv_imagenes(lista):
    if not lista: return
    keys = ['nombre', 'url_imagen']
    with open('jugadores_imagenes.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(lista)


if __name__ == "__main__":
    ejecutar()