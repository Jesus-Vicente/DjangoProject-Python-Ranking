import requests
from bs4 import BeautifulSoup

# 1. La URL de la categoría de personajes de la T1
url = "https://inazuma.fandom.com/es/wiki/Categoría:Personajes_(IE_Original_T1)"

# 2. Hacemos la petición a la web
respuesta = requests.get(url)

# 3. Parseamos el HTML
soup = BeautifulSoup(respuesta.text, 'html.parser')

# 4. Buscamos los elementos que contienen los nombres
# En Fandom, los nombres suelen estar en enlaces dentro de una clase específica
personajes = soup.find_all('a', class_='category-page__member-link')

print(f"He encontrado {len(personajes)} personajes:\n")

for p in personajes:
    nombre = p.text.strip()
    # Filtramos para que no salgan cosas raras
    if "Categoría" not in nombre:
        print(f"- {nombre}")