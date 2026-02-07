import cloudscraper
from bs4 import BeautifulSoup
import csv
import time
import random


def extraer_datos_jugador(url, scraper):
    try:
        time.sleep(random.uniform(3.0, 5.0))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Referer': 'https://inazuma.fandom.com/',
        }

        response = scraper.get(url, headers=headers, timeout=15)
        if response.status_code != 200: return "BLOQUEO"

        soup = BeautifulSoup(response.text, 'html.parser')
        header = soup.find('h1', id='firstHeading')
        if not header: return "BLOQUEO"

        nombre = header.text.strip()
        datos = {'nombre': nombre, 'afinidad': 'N/A', 'posicion': 'N/A', 'equipo': 'N/A'}

        for item in soup.select('.pi-item.pi-data'):
            source = item.get('data-source', '').lower()
            value = item.find(class_='pi-data-value')
            if value:
                txt = value.get_text(" ", strip=True).split('(')[0].strip()
                if 'elemento' in source or 'afinidad' in source:
                    datos['afinidad'] = txt
                elif 'posici' in source or 'demarcaci' in source:
                    datos['posicion'] = txt
                elif 'equipo' in source:
                    datos['equipo'] = txt

        return datos
    except Exception:
        return "ERROR"


def ejecutar():
    scraper = cloudscraper.create_scraper(
        browser={
            'custom': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'}
    )

    url_actual = "https://inazuma.fandom.com/es/wiki/Categor%C3%ADa:Personajes_(IE_Original_T1)"
    urls_totales = []

    print("--- 🔍 Buscando todas las URLs (Página 1, 2...) ---")

    # BUCLE PARA NAVEGAR POR LA PAGINACIÓN DE LA CATEGORÍA
    while url_actual:
        try:
            res_cat = scraper.get(url_actual)
            soup_cat = BeautifulSoup(res_cat.text, 'html.parser')

            # Extraer enlaces de la página actual
            enlaces = ["https://inazuma.fandom.com" + a['href'] for a in soup_cat.select('.category-page__member-link')]
            urls_totales.extend(enlaces)

            print(f"✅ Capturadas {len(enlaces)} URLs de esta página...")

            # Buscar el botón "Siguiente"
            boton_siguiente = soup_cat.select_one('a.category-page__pagination-next')
            if boton_siguiente and 'href' in boton_siguiente.attrs:
                url_actual = boton_siguiente['href']
            else:
                url_actual = None  # No hay más páginas
        except Exception as e:
            print(f"Error buscando páginas: {e}")
            break

    print(f"--- Total de personajes encontrados: {len(urls_totales)} ---")

    resultados = []
    print("\n" + "=" * 85)
    print(f"{'#':<4} | {'NOMBRE':<25} | {'ELEMENTO':<12} | {'POSICIÓN':<15} | {'EQUIPO'}")
    print("-" * 85)

    for i, url in enumerate(urls_totales):
        info = extraer_datos_jugador(url, scraper)

        if info == "BLOQUEO":
            print(f"[{i + 1}] ⛔ ERROR: Bloqueo de Cloudflare.")
            break

        if isinstance(info, dict):
            print(
                f"{i + 1:<4} | {info['nombre'][:25]:<25} | {info['afinidad']:<12} | {info['posicion']:<15} | {info['equipo']}")
            resultados.append(info)
        else:
            print(f"{i + 1:<4} | ❌ Error en {url.split('/')[-1]}")

        if (i + 1) % 10 == 0:
            guardar_csv(resultados)

    guardar_csv(resultados)
    print(f"\n✅ Proceso terminado. Total final: {len(resultados)} personajes.")


def guardar_csv(lista):
    if not lista: return
    with open('jugadores_datos.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['nombre', 'afinidad', 'posicion', 'equipo'])
        writer.writeheader()
        writer.writerows(lista)


if __name__ == "__main__":
    ejecutar()