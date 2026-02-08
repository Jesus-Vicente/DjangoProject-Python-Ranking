import pandas as pd
import re
import json


def limpiar_lista_equipos(texto_sucio):
    if pd.isna(texto_sucio) or texto_sucio == "N/A":
        return []

    # 1. Quitamos ruidos comunes de la Wiki como "1ª Línea :", "Línea Original :", etc.
    limpio = re.sub(r'(1ª|2ª|Línea)\s*\w*\s*[:\-]', '', texto_sucio)

    # 2. Separamos por patrones de la wiki (números con punto "7. " o interrogaciones "??. ")
    # También separamos si detectamos nombres de equipos pegados
    partes = re.split(r'\d+\.\s*|\?\?\.\s*', limpio)

    # 3. Limpieza final de cada equipo en la lista
    equipos_finales = []
    for p in partes:
        nombre_equipo = p.strip()
        # Filtramos nombres vacíos o demasiado cortos
        if nombre_equipo and len(nombre_equipo) > 2:
            # Si el equipo tiene un "[ 1 ]", lo quitamos
            nombre_equipo = re.sub(r'\[\s*\d+\s*\]', '', nombre_equipo).strip()
            equipos_finales.append(nombre_equipo)

    return list(set(equipos_finales))  # set() elimina duplicados si los hubiera


def procesar_para_nosql():
    print("--- 🧹 Limpiando datos para formato NoSQL ---")
    df = pd.read_csv('personajes_final.csv')

    # Aplicamos la limpieza a la columna equipo
    df['equipo'] = df['equipo'].apply(limpiar_lista_equipos)

    # Opcional: Limpiar también la posición (por si viene con "[ 1 ]")
    df['posicion'] = df['posicion'].apply(lambda x: re.sub(r'\[\s*\d+\s*\]', '', str(x)).strip())

    # Guardar como JSON (el formato rey de NoSQL)
    df.to_json('personajes_nosql.json', orient='records', force_ascii=False, indent=4)

    print("✅ ¡Listo! Se ha creado 'personajes_nosql.json'")
    print("Muestra del primer registro:")
    print(df.iloc[20].to_dict())  # Mostramos a un jugador con varios equipos para probar


if __name__ == "__main__":
    procesar_para_nosql()