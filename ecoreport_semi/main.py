# Creado por Alejandro Venegas Robles.
# En caso de incidencias, contactar con alejandro2196vr@gmail.com
# -*- coding: utf-8 -*-
"""
Sistema de Informes de Ecocardioscopia Clínica
Basado en los parámetros de la SEMI para evaluación ecocardiográfica a pie de cama.
"""

import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.error_handling import setup_exception_handling, log_message

def main():
    """Punto de entrada principal de la aplicación."""
    # --- INICIO: Marcador para localización de errores (Configuración Global) ---
    setup_exception_handling()
    # --- FIN: Marcador para localización de errores (Configuración Global) ---
    try:
        log_message("Iniciando la aplicación EcoReport SEMI.", "info")
        
        app = QApplication(sys.argv)
        app.setApplicationName("EcoReport SEMI")
        app.setApplicationVersion("1.0.0") # Puedes obtener esto de config.py

        main_window = MainWindow()
        main_window.show()
        
        log_message("Ventana principal mostrada. Iniciando bucle de eventos.", "info")
        sys.exit(app.exec_())
        
    except SystemExit:
        log_message("Aplicación cerrada limpiamente.", "info")
    except Exception as e:
        # Esta captura es un último recurso, idealmente manejado por sys.excepthook
        log_message(f"Error catastrófico no capturado en main: {e}", "critical", exc_info=True)
        # Aquí podrías mostrar un QMessageBox simple si el error_handling falló completamente
        return 1

if __name__ == "__main__":
    main()