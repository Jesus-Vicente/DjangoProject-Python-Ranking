import cloudscraper
from bs4 import BeautifulSoup
import csv
import time
import random


def extraer_imagen_jugador(url, scraper):
    try:
        time.sleep(random.uniform(1.5, 3.0))
        res = scraper.get(url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        nombre = soup.find('h1', id='firstHeading').text.strip()

        # Estrategia: Buscar en la Infobox el tag de imagen
        img_tag = soup.select_one('aside.portable-infobox img.pi-image-thumbnail')
        img_url = "N/A"

        if img_tag:
            # Captura data-src (lazy load) o src normal
            img_url = img_tag.get('data-src') or img_tag.get('src')
            if img_url:
                # Limpieza radical: eliminamos todo tras la extensión del archivo
                img_url = img_url.split('/revision')[0]

        return {'nombre': nombre, 'url_imagen': img_url}
    except:
        return None


def ejecutar():
    scraper = cloudscraper.create_scraper()
    url_cat = "https://inazuma.fandom.com/es/wiki/Categor%C3%ADa:Personajes_(IE_Original_T1)"

    print("--- 🖼️ Extrayendo IMÁGENES de personajes ---")
    res_cat = scraper.get(url_cat)
    soup_cat = BeautifulSoup(res_cat.text, 'html.parser')
    enlaces = ["https://inazuma.fandom.com" + a['href'] for a in soup_cat.select('.category-page__member-link')]

    resultados = []
    for i, url in enumerate(enlaces[:200]):
        info = extraer_imagen_jugador(url, scraper)
        if info:
            print(f"[{i + 1}] URL Imagen: {info['nombre']}")
            resultados.append(info)

    with open('jugadores_imagenes.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['nombre', 'url_imagen'])
        writer.writeheader()
        writer.writerows(resultados)
    print("✅ Archivo 'jugadores_imagenes.csv' creado.")


if __name__ == "__main__": ejecutar()