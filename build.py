# Creado por Alejandro Venegas Robles.
# En caso de incidencias, contactar con alejandro2196vr@gmail.com
# -*- coding: utf-8 -*-
"""
Script para generar el ejecutable de EcoReport SEMI usando PyInstaller.
"""
import os
import subprocess
import shutil
import sys

APP_NAME = "EcoReportSEMI"
ENTRY_POINT = "main.py" # Script principal de la aplicación
ICON_FILE = os.path.join("resources", "icon.ico") # Asegúrate que este archivo exista

def check_dependencies():
    """Verifica e intenta instalar dependencias faltantes."""
    dependencies = {"PyQt5": "PyQt5", "PyInstaller": "pyinstaller"}
    missing = []
    for lib_import, lib_install in dependencies.items():
        try:
            __import__(lib_import)
            print(f"{lib_import} ya está instalado.")
        except ImportError:
            print(f"{lib_import} no está instalado.")
            missing.append(lib_install)
    
    if missing:
        print(f"Intentando instalar dependencias faltantes: {', '.join(missing)}")
        for lib_install in missing:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib_install])
                print(f"{lib_install} instalado correctamente.")
            except subprocess.CalledProcessError as e:
                print(f"Error al instalar {lib_install}: {e}")
                print("Por favor, instale las dependencias manualmente y reintente.")
                return False
    return True


def build_executable():
    """Construye el ejecutable con PyInstaller."""
    print(f"Construyendo el ejecutable de {APP_NAME}...")

    # Limpiar directorios de construcción anteriores
    for dir_to_clean in ['build', 'dist', f"{APP_NAME}.spec"]:
        if os.path.exists(dir_to_clean):
            print(f"Limpiando: {dir_to_clean}")
            if os.path.isdir(dir_to_clean):
                shutil.rmtree(dir_to_clean)
            else:
                os.remove(dir_to_clean)

    # Opciones de PyInstaller
    pyinstaller_options = [
        'pyinstaller',
        '--name', APP_NAME,
        '--windowed',  # Aplicación GUI, sin consola al ejecutar
        '--onefile',   # Un solo archivo ejecutable
        # '--noconfirm', # Sobrescribir sin preguntar
    ]

    if os.path.exists(ICON_FILE):
        pyinstaller_options.extend(['--icon', ICON_FILE])
    else:
        print(f"Advertencia: Archivo de icono no encontrado en {ICON_FILE}. Se usará el icono por defecto.")

       # Para incluir la carpeta 'resources'
    # La ruta a 'resources' debe ser relativa al script build.py o absoluta.
    # Si build.py está en la raíz de ecoreport_semi, y resources también:
    resources_path = "resources" 
    if os.path.exists(resources_path):
        # El formato es "origen:destino_en_bundle" o "origen;destino_en_bundle" en Windows
        # PyInstaller usa ':' como separador universal en la opción, y lo adapta.
        # Si resources_path = "resources", y quieres que en el bundle esté como "resources":
        pyinstaller_options.extend(['--add-data', f"{resources_path}{os.pathsep}resources"])
        print(f"Incluyendo datos de la carpeta: {resources_path}")
    else:
        print(f"Advertencia: Carpeta de recursos no encontrada en {resources_path}. No se añadirán datos extra.")
        
    pyinstaller_options.append(ENTRY_POINT)

    print(f"\nEjecutando PyInstaller con las siguientes opciones:\n{' '.join(pyinstaller_options)}\n")
    
    try:
        process = subprocess.Popen(pyinstaller_options, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            print("\n--- Salida de PyInstaller (stdout) ---")
            print(stdout)
            print(f"\nEjecutable construido correctamente en: dist/{APP_NAME}.exe")
            return True
        else:
            print("\n--- Error al construir el ejecutable ---")
            print("--- Salida de PyInstaller (stdout) ---")
            print(stdout)
            print("\n--- Salida de PyInstaller (stderr) ---")
            print(stderr)
            return False
            
    except FileNotFoundError:
        print("Error: PyInstaller no se encontró en el PATH del sistema.")
        print("Asegúrese de que PyInstaller está instalado y accesible.")
        return False
    except Exception as e:
        print(f"Error inesperado durante la ejecución de PyInstaller: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando proceso de construcción para EcoReport SEMI...")
    if not check_dependencies():
        print("\nProceso de construcción detenido debido a dependencias faltantes.")
        sys.exit(1)

    if build_executable():
        print("\nProceso de construcción completado con éxito.")
    else:
        print("\nEl proceso de construcción falló.")
        sys.exit(1)