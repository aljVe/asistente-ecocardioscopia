# Creado por Alejandro Venegas Robles.
# En caso de incidencias, contactar con alejandro2196vr@gmail.com
# -*- coding: utf-8 -*-
"""
Utilidades para el manejo de errores y logging en EcoReport SEMI.
"""
import sys
import traceback
import logging
import os
from PyQt5.QtWidgets import QMessageBox
import config # Para LOG_FILE_PATH

_logger = None

def _get_logger():
    global _logger
    if _logger is None:
        # --- INICIO: Marcador para localización de errores (Config Logger) ---
        try:
            _logger = logging.getLogger("EcoReportSEMI")
            _logger.setLevel(logging.DEBUG) # Nivel mínimo para capturar todo

            # Evitar añadir manejadores múltiples si se llama varias veces (aunque no debería)
            if not _logger.handlers:
                # Formateador
                formatter = logging.Formatter(
                    "%(asctime)s [%(levelname)-8s] %(module)-15s:%(lineno)-4d - %(message)s"
                )
                
                # Manejador para archivo
                file_handler = logging.FileHandler(config.LOG_FILE_PATH, encoding='utf-8', mode='a')
                file_handler.setFormatter(formatter)
                file_handler.setLevel(logging.DEBUG) # Loguear todo a archivo
                _logger.addHandler(file_handler)

                # Manejador para consola (opcional, para desarrollo)
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setFormatter(formatter)
                console_handler.setLevel(logging.INFO) # Loguear INFO y superior a consola
                _logger.addHandler(console_handler)
            
            _logger.info(f"Logger 'EcoReportSEMI' configurado. Log en: {config.LOG_FILE_PATH}")
        except Exception as e:
            # Error configurando el logger, usar print como fallback
            print(f"CRITICAL: Error configurando el logger: {e}\n{traceback.format_exc()}")
            # Configurar un logger básico como fallback si todo falla
            logging.basicConfig(level=logging.DEBUG)
            _logger = logging.getLogger("EcoReportSEMI_fallback")
            _logger.error(f"Fallback logger activado debido a error: {e}")
        # --- FIN: Marcador para localización de errores (Config Logger) ---
    return _logger

def log_message(message: str, level: str = "info", exc_info=False):
    """Registra un mensaje usando el logger de la aplicación."""
    logger = _get_logger()
    if level == "debug":
        logger.debug(message, exc_info=exc_info)
    elif level == "info":
        logger.info(message, exc_info=exc_info)
    elif level == "warning":
        logger.warning(message, exc_info=exc_info)
    elif level == "error":
        logger.error(message, exc_info=exc_info)
    elif level == "critical":
        logger.critical(message, exc_info=exc_info)

def _handle_exception(exc_type, exc_value, exc_traceback):
    """Manejador para excepciones no capturadas (sys.excepthook)."""
    # --- INICIO: Marcador para localización de errores (Handle Exception Global) ---
    # Registrar la excepción con todos los detalles usando el logger
    log_message(
        "Excepción global no capturada:",
        level="critical",
        exc_info=(exc_type, exc_value, exc_traceback) # Pasa la tupla de excepción
    )

    # Formatear el mensaje de error para el usuario
    # La información detallada de la línea de código ya está en el log
    error_msg_user = f"Se ha producido un error inesperado en la aplicación.\n\n"
    error_msg_user += f"Tipo: {exc_type.__name__}\n"
    error_msg_user += f"Mensaje: {str(exc_value)}\n\n"
    error_msg_user += "Se recomienda guardar su trabajo si es posible y reiniciar la aplicación.\n"
    error_msg_user += "Los detalles completos del error han sido registrados en el archivo de log."

    # Para obtener la info de la última llamada para el detailedText del QMessageBox
    tb_info_list = traceback.extract_tb(exc_traceback)
    detailed_text_for_user = "Detalles técnicos (última llamada):\n"
    if tb_info_list:
        filename, line_no, func_name, source_code = tb_info_list[-1]
        detailed_text_for_user += f"  Archivo: {os.path.basename(filename)}\n"
        detailed_text_for_user += f"  Línea: {line_no} en función '{func_name}'\n"
        if source_code:
            detailed_text_for_user += f"  Código: {source_code.strip()}\n"
    detailed_text_for_user += "\nConsulte el archivo de log para la traza completa."

    # Mostrar diálogo de error
    # No se debe crear QApplications o QWidgets directamente en un excepthook si puede ser llamado
    # antes de que QApplication esté inicializado o desde un hilo no GUI.
    # Sin embargo, si QApplication ya está corriendo, es generalmente seguro.
    # Para mayor robustez, se podría emitir una señal a la ventana principal para que ella muestre el diálogo.
    # Aquí asumimos que QApplication está activo.
    if QMessageBox is not None: # Verificar si el módulo está disponible
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error Crítico en la Aplicación")
        msg_box.setText(error_msg_user)
        # msg_box.setInformativeText("Consulte el log para detalles técnicos.") # Ya incluido en el texto principal
        msg_box.setDetailedText(detailed_text_for_user) # Para que el usuario pueda expandir
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    else: # Fallback si QMessageBox no está disponible (ej. error muy temprano)
        print("CRITICAL ERROR (QMessageBox not available):\n", error_msg_user)
        print(detailed_text_for_user)

    # --- FIN: Marcador para localización de errores (Handle Exception Global) ---


def setup_exception_handling():
    """Configura el manejador global de excepciones."""
    _get_logger() # Asegurar que el logger está inicializado
    sys.excepthook = _handle_exception
    log_message("Manejador de excepciones global configurado.", "info")