# Creado por Alejandro Venegas Robles.
# En caso de incidencias, contactar con alejandro2196vr@gmail.com
# -*- coding: utf-8 -*-
"""
Configuraciones y constantes para la aplicación EcoReport SEMI.
Valores de referencia basados en el infograma SEMI 'ecoscopia_en_icc_v05.pdf'.
"""
import os
import sys
from datetime import datetime

# --- Definición de Rutas Base ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) 
# RESOURCES_DIR_DEV debe apuntar a ecoreport_semi/resources
RESOURCES_DIR_DEV = os.path.join(PROJECT_ROOT, "resources")
LOG_DIR = os.path.join(PROJECT_ROOT, "logs") # Directorio para logs

# Asegurar que el directorio de logs existe
if not os.path.exists(LOG_DIR):
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except OSError as e:
        print(f"Advertencia: No se pudo crear el directorio de logs en {LOG_DIR}: {e}")
        # Fallback al directorio actual si falla la creación en la ubicación preferida
        LOG_DIR = os.path.join(os.getcwd(), "ecoreport_semi_logs") # Evitar conflicto si ya existe 'logs'
        try:
            os.makedirs(LOG_DIR, exist_ok=True)
            print(f"Usando directorio de logs alternativo: {LOG_DIR}")
        except OSError as e_fallback:
            print(f"CRÍTICO: No se pudo crear el directorio de logs. Error: {e_fallback}")
            # Considerar terminar la app o usar una estrategia de no-logging.
            # Por ahora, se continuará y el logger podría fallar.
            pass

# --- FUNCIÓN HELPER PARA RUTAS DE RECURSOS ---
def resource_path(relative_path: str) -> str:
    """
    Obtiene la ruta absoluta a un recurso, funciona para desarrollo y para PyInstaller.
    Asume que los recursos están en una carpeta 'resources' al mismo nivel que este
    archivo config.py (si estás en desarrollo) o en una carpeta 'resources'
    dentro del bundle de PyInstaller.
    """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en sys._MEIPASS
        # Los recursos se empaquetaron en una subcarpeta 'resources' dentro de _MEIPASS
        base_path = os.path.join(sys._MEIPASS, "resources")
    except AttributeError:
        # sys._MEIPASS no está definido, así que estamos en desarrollo
        base_path = RESOURCES_DIR_DEV # Usa la ruta de desarrollo

    return os.path.join(base_path, relative_path)

LOG_FILE_PATH = os.path.join(LOG_DIR, f"ecoreport_log_{datetime.now().strftime('%Y%m%d')}.log")

# --- Información de la Aplicación ---
APP_VERSION = "1.0.0"
APP_NAME = "EcoReport SEMI"
APP_AUTHOR_SIGNATURE = "Creado por Alejandro Venegas Robles. Contacto: alejandro2196vr@gmail.com"

# --- Opcional: Ruta al Icono ---
# Descomenta y ajusta si tienes un icono. Debe estar en la carpeta 'resources'.
# ICON_PATH = os.path.join(RESOURCES_DIR, "ecoreport_icon.ico") # Ejemplo

# === VALORES DE REFERENCIA ECOCARDIOGRÁFICOS (Según Infograma SEMI) ===

# --- Ventrículo Izquierdo (VI) ---
SEPTUM_MAX_MASC = 11  # mm
SEPTUM_MAX_FEM = 10   # mm
PARED_POST_MAX_MASC = 11 # mm
PARED_POST_MAX_FEM = 10  # mm
DTDVI_MAX_MASC = 58   # mm
DTDVI_MAX_FEM = 52    # mm
FEVI_REDUCIDA_MAX = 40  # % (≤40%)
FEVI_LIGERAMENTE_REDUCIDA_MAX = 49 # % (41-49%)

# --- Aurícula Izquierda (AI) ---
AI_VOL_IDX_NORMAL_MAX_RS = 34  # ml/m² (Ritmo Sinusal, ≤34)
AI_VOL_IDX_DILATADA_MIN_FA_O_ICFEVIP = 34 # ml/m² (>34 en FA o para criterio IC FEVIp)

# --- Ventrículo Derecho (VD) ---
VD_DIAMETRO_BASAL_MAX = 42 # mm (≤42 mm)
TAPSE_NORMAL_MIN = 17 # mm (>17 mm)

# --- Doppler y Presiones de Llenado VI ---
E_A_NORMAL_MAX = 0.8 # Mitral E/A ≤0.8 -> Presiones normales
E_A_ELEVADA_MIN = 2.0 # Mitral E/A ≥2 -> Presiones elevadas
E_E_PRIMA_CORTE_PRESIONES = 14 # E/e' > 14
# AI_VOL_IDX_CORTE_PRESIONES ya definido como AI_VOL_IDX_DILATADA_MIN_FA_O_ICFEVIP
IT_VELOCIDAD_CORTE_PRESIONES = 2.8 # Vel IT >2.8 m/s
VELOCIDAD_AORTICA_ESTENOSIS_SEVERA = 4.0 # m/s (EAo severa)
# IT_VELOCIDAD_MAX_HTP ya definido como IT_VELOCIDAD_CORTE_PRESIONES

# --- Derrames ---
DERRPER_LEVE_MAX = 10 # mm (Derrame Pericárdico Leve ≤10mm)
DERRPER_MODERADO_MAX = 20 # mm (Derrame Pericárdico Moderado 10-20mm)

# --- Congestión Pulmonar ---
LINEAS_B_PATOLOGICAS_MIN_POR_ESPACIO = 3 # >3 por espacio

# --- Congestión Sistémica (VCI y VExUS) ---
VCI_DIAMETRO_PATOLOGICO_PVC = 21 # mm (>21 mm Y colapso <50%)
VCI_COLAPSO_INSPIRATORIO_MIN_NORMAL_PVC = 50 # % (<50% con VCI >21mm)
VCI_DIAMETRO_CORTE_VEXUS = 20 # mm (>20mm para VExUS)

VSH_PATRONES = ["Normal (S>D)", "Leve (S<D)", "Grave (Onda S invertida)"] #
VP_PATRONES = ["Normal (Continuo, Pulsatilidad <30%)", "Leve (Pulsatilidad 30-49%, Bifásico S-D)", "Grave (Pulsatilidad ≥50%, Monofásico S-D)"] #
VIR_PATRONES = ["Normal (Continuo)", "Leve (Bifásico S-D)", "Grave (Monofásico S-D)"] #

# --- Nombres Descriptivos para Secciones (Referencia, no usado activamente ahora) ---
CHECKLIST_ITEMS_NOMBRES_DESCRIPTIVOS = {
    "HVI_VI": "Hipertrofia Ventrículo Izquierdo",
    "TAM_VI_AI": "Tamaño Ventrículo y Aurícula Izquierda",
    "CAV_DER": "Cavidades Derechas y Función VD (TAPSE)",
    "VALVULOPATIAS": "Valvulopatías Significativas",
    "FEVI_PRESIONES_VI": "Función Sistólica y Presiones de Llenado VI",
    "DERR_PERIC": "Derrame Pericárdico",
    "DERR_PLEURAL": "Derrame Pleural",
    "LINEAS_B": "Líneas B (Congestión Pulmonar)",
    "VCI": "Vena Cava Inferior",
    "VEXUS": "Score VExUS (Congestión Sistémica)"
}