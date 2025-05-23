# Creado por Alejandro Venegas Robles.
# En caso de incidencias, contactar con alejandro2196vr@gmail.com
# -*- coding: utf-8 -*-
"""
Ventana principal de la aplicación EcoReport SEMI.
"""
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QStatusBar, QAction, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon # Asegúrate que QIcon está importado

import config
from models import InformeEcoCompleto
# Importar la NUEVA Pestaña Unificada
from .tabs.datos_eco_tab import DatosEcoTab # NUEVA IMPORTACIÓN
# YA NO SE IMPORTAN LAS PESTAÑAS ANTIGUAS
# from .tabs.eco_basica_tab import EcoBasicaTab
# from .tabs.eco_avanzada_tab import EcoAvanzadaTab
# from .tabs.congestion_tab import CongestionTab
from .tabs.informe_tab import InformeTab # Esta se mantiene

from logic.report_generator import generar_informe_texto
from utils.error_handling import log_message

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            log_message("Inicializando MainWindow.", "debug")
            self.current_informe = InformeEcoCompleto()
            self.init_ui()
            log_message("UI de MainWindow inicializada.", "debug")
        except Exception as e:
            log_message(f"Error crítico inicializando MainWindow: {e}", "critical", exc_info=True)
            QMessageBox.critical(self, "Error Crítico", 
                                 f"No se pudo inicializar la ventana principal: {e}\n"
                                 "Consulte el log para más detalles.")

    def init_ui(self):
        self.setWindowTitle(f"EcoReport SEMI v{config.APP_VERSION}")
        self.setMinimumSize(1024, 768) # Ajusta según necesidad
        # Para el icono, asegúrate de tener un archivo 'icon.ico' en la carpeta 'resources'
        # y que config.py tenga una variable ICON_PATH = "resources/icon.ico" o similar
        icon_path = getattr(config, 'ICON_PATH', None) # getattr para evitar error si no existe
        if icon_path and QIcon.hasThemeIcon(icon_path): # o if os.path.exists(icon_path):
             self.setWindowIcon(QIcon(icon_path))
        elif icon_path:
             log_message(f"Icono no encontrado o no válido: {icon_path}", "warning")


        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu("&Archivo")
        
        nuevo_action = QAction("&Nuevo Informe", self)
        nuevo_action.triggered.connect(self.nuevo_informe)
        file_menu.addAction(nuevo_action)
        
        exportar_action = QAction("&Exportar Informe Texto...", self)
        exportar_action.triggered.connect(self.exportar_informe_texto)
        file_menu.addAction(exportar_action)

        file_menu.addSeparator()
        exit_action = QAction("&Salir", self)
        exit_action.triggered.connect(self.close) # self.close llama a closeEvent
        file_menu.addAction(exit_action)
        
        help_menu = self.menu_bar.addMenu("A&yuda")
        about_action = QAction("&Acerca de", self)
        about_action.triggered.connect(self.mostrar_acerca_de)
        help_menu.addAction(about_action)

        self.tabs_widget = QTabWidget()
        
        # Crear e instanciar la nueva pestaña unificada
        self.datos_eco_tab = DatosEcoTab(self.current_informe) # NUEVA PESTAÑA
        
        # La pestaña de informe final se mantiene
        self.informe_final_tab = InformeTab(self.current_informe, self) # Pasar self (MainWindow)

        self.tabs_widget.addTab(self.datos_eco_tab, "Datos Ecocardiográficos") # NOMBRE DE LA NUEVA PESTAÑA
        self.tabs_widget.addTab(self.informe_final_tab, "Informe Final y Acciones")

        self.setCentralWidget(self.tabs_widget)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo. " + config.APP_AUTHOR_SIGNATURE, 5000)

    @pyqtSlot()
    def nuevo_informe(self):
        try:
            log_message("Acción: Nuevo Informe seleccionada.", "info")
            respuesta = QMessageBox.question(self, "Nuevo Informe",
                                             "¿Desea borrar los datos actuales y empezar un nuevo informe?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if respuesta == QMessageBox.Yes:
                self.current_informe = InformeEcoCompleto()
                # Actualizar las pestañas con el nuevo modelo vacío
                self.datos_eco_tab.set_modelo(self.current_informe) # ACTUALIZADO
                self.informe_final_tab.set_modelo(self.current_informe)
                self.status_bar.showMessage("Nuevo informe iniciado.", 3000)
                log_message("Nuevo informe creado. Campos reiniciados.", "info")
        except Exception as e:
            log_message(f"Error al crear nuevo informe: {e}", "error", exc_info=True)
            QMessageBox.warning(self, "Error", f"No se pudo reiniciar el informe: {e}")

    def _actualizar_modelo_desde_ui(self):
        """Método para asegurar que el modelo central tiene los datos de la UI."""
        log_message("Actualizando modelo central desde UI antes de generar informe.", "debug")
        if hasattr(self.datos_eco_tab, 'actualizar_modelo'): # ACTUALIZADO
            self.datos_eco_tab.actualizar_modelo()
        if hasattr(self.informe_final_tab, 'actualizar_modelo'): # Para "Realizado por" y "Comentarios"
            self.informe_final_tab.actualizar_modelo()

    @pyqtSlot()
    def exportar_informe_texto(self):
        try:
            log_message("Acción: Exportar Informe Texto seleccionada.", "info")
            self._actualizar_modelo_desde_ui() # Asegurar datos actualizados
            
            informe_texto_generado = generar_informe_texto(self.current_informe)
            self.informe_final_tab.mostrar_informe_texto(informe_texto_generado) # Actualizar preview

            opciones = QFileDialog.Options()
            # opciones |= QFileDialog.DontUseNativeDialog # Comentar si prefieres diálogo nativo
            default_filename = f"EcoInforme_{self.current_informe.id_informe}.txt"
            nombre_archivo, _ = QFileDialog.getSaveFileName(self, "Guardar Informe como Texto", 
                                                           default_filename,
                                                           "Archivos de Texto (*.txt);;Todos los Archivos (*)", 
                                                           options=opciones)
            if nombre_archivo:
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    f.write(informe_texto_generado)
                self.status_bar.showMessage(f"Informe guardado en: {nombre_archivo}", 5000)
                log_message(f"Informe de texto exportado a: {nombre_archivo}", "info")
        except Exception as e:
            log_message(f"Error al exportar informe de texto: {e}", "error", exc_info=True)
            QMessageBox.critical(self, "Error de Exportación", f"No se pudo exportar el informe: {e}")
            
    @pyqtSlot()
    def mostrar_acerca_de(self):
        try:
            log_message("Mostrando diálogo 'Acerca de'.", "info")
            QMessageBox.about(self, "Acerca de EcoReport SEMI",
                              f"EcoReport SEMI v{config.APP_VERSION}\n\n"
                              "Sistema de generación de informes de ecocardioscopia clínica "
                              "basado en los parámetros de la SEMI.\n\n"
                              f"{config.APP_AUTHOR_SIGNATURE}")
        except Exception as e:
            log_message(f"Error al mostrar 'Acerca de': {e}", "error", exc_info=True)

    def closeEvent(self, event):
        try:
            log_message("Evento closeEvent detectado. Cerrando aplicación sin confirmación.", "info")
            event.accept()
        except Exception as e:
            log_message(f"Error durante closeEvent: {e}", "error", exc_info=True)
            event.accept()