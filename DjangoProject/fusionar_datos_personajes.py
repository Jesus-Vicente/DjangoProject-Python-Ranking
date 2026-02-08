import pandas as pd


def fusionar_csv():
    print("--- 🔄 Fusionando archivos de datos e imágenes ---")

    try:
        # Cargamos ambos archivos
        df_datos = pd.read_csv('jugadores_datos.csv')
        df_imagenes = pd.read_csv('jugadores_imagenes.csv')

        # Fusionamos usando la columna 'nombre' como clave común
        # Usamos 'left' para asegurar que mantenemos todos los personajes de la lista de datos
        df_final = pd.merge(df_datos, df_imagenes, on='nombre', how='left')

        # Guardamos el resultado final
        df_final.to_csv('personajes_final.csv', index=False, encoding='utf-8')

        print(f"✅ ¡Éxito! Se han unido {len(df_final)} personajes.")
        print("📁 Archivo creado: 'personajes_final.csv'")

        # Mostrar una pequeña muestra del resultado
        print("\n--- Vista previa de los datos ---")
        print(df_final.head())

    except FileNotFoundError:
        print("❌ Error: No se encontraron los archivos .csv. Asegúrate de que estén en la misma carpeta.")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")


if __name__ == "__main__":
    fusionar_csv()