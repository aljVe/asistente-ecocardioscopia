# Creado por Alejandro Venegas Robles.
# En caso de incidencias, contactar con alejandro2196vr@gmail.com
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit, 
                             QPushButton, QGroupBox, QFormLayout, QLineEdit, QHBoxLayout, QApplication) # Añadido QHBoxLayout, QApplication
from PyQt5.QtCore import pyqtSlot
from models import InformeEcoCompleto
from utils.error_handling import log_message
from logic.report_generator import generar_informe_texto # Necesario para el botón de preview

class InformeTab(QWidget):
    def __init__(self, modelo_informe: InformeEcoCompleto, main_window_ref, parent=None): # main_window_ref para llamar a _actualizar_modelo_desde_ui
        super().__init__(parent)
        self.modelo_informe = modelo_informe
        self.main_window = main_window_ref # Guardar referencia a la ventana principal
        self._init_ui()
        self._conectar_senales()
        self.cargar_modelo_en_ui()
        log_message("Pestaña InformeTab inicializada con campos y botones.", "debug")

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        
        meta_group = QGroupBox("Metadatos del Informe")
        meta_form_layout = QFormLayout()
        self.realizado_por_edit = QLineEdit()
        meta_form_layout.addRow("Realizado por:", self.realizado_por_edit)
        self.comentarios_edit = QTextEdit()
        self.comentarios_edit.setPlaceholderText("Anotaciones o conclusiones adicionales...")
        self.comentarios_edit.setFixedHeight(80)
        meta_form_layout.addRow("Comentarios Adicionales:", self.comentarios_edit)
        meta_group.setLayout(meta_form_layout)
        main_layout.addWidget(meta_group)

        preview_group = QGroupBox("Informe Final")
        preview_layout_v = QVBoxLayout() # Layout vertical para este grupo
        
        # Layout para botones
        botones_layout_h = QHBoxLayout() # Layout horizontal para botones
        self.btn_generar_preview = QPushButton("Generar/Actualizar Previsualización")
        botones_layout_h.addWidget(self.btn_generar_preview)
        self.btn_copiar_informe = QPushButton("Copiar Informe al Portapapeles")
        botones_layout_h.addWidget(self.btn_copiar_informe)
        botones_layout_h.addStretch() # Empuja los botones a la izquierda
        preview_layout_v.addLayout(botones_layout_h) # Añadir layout de botones primero

        self.texto_informe_display = QTextEdit("Pulse 'Generar/Actualizar Previsualización' para ver el informe.")
        self.texto_informe_display.setReadOnly(True)
        preview_layout_v.addWidget(self.texto_informe_display) # Añadir el display del texto después
        
        preview_group.setLayout(preview_layout_v)
        main_layout.addWidget(preview_group)
        main_layout.setStretchFactor(preview_group, 1)

        self.setLayout(main_layout)

    def _conectar_senales(self):
        self.realizado_por_edit.editingFinished.connect(self.actualizar_modelo_meta)
        self.comentarios_edit.textChanged.connect(self.actualizar_modelo_meta)
        
        self.btn_generar_preview.clicked.connect(self.on_generar_preview_clicked)
        self.btn_copiar_informe.clicked.connect(self.on_copiar_informe_clicked)

    def actualizar_modelo_meta(self): # Actualiza solo los metadatos de esta pestaña
        self.modelo_informe.realizado_por = self.realizado_por_edit.text().strip()
        self.modelo_informe.comentarios_adicionales = self.comentarios_edit.toPlainText().strip()
        log_message("Metadatos de InformeTab actualizados.", "debug")

    def cargar_modelo_en_ui(self):
        self.realizado_por_edit.setText(self.modelo_informe.realizado_por or "")
        self.comentarios_edit.setPlainText(self.modelo_informe.comentarios_adicionales or "")
        self.mostrar_informe_texto("Pulse 'Generar/Actualizar Previsualización' para ver el informe.")

    def set_modelo(self, nuevo_modelo_informe: InformeEcoCompleto):
        self.modelo_informe = nuevo_modelo_informe
        self.cargar_modelo_en_ui()
        log_message("Modelo general recargado en InformeTab.", "debug")

    def mostrar_informe_texto(self, texto: str):
        self.texto_informe_display.setPlainText(texto)

    @pyqtSlot()
    def on_generar_preview_clicked(self):
        try:
            log_message("Botón 'Generar/Actualizar Previsualización' pulsado.", "info")
            # Asegurar que el modelo principal está actualizado desde DatosEcoTab
            if hasattr(self.main_window, '_actualizar_modelo_desde_ui'):
                self.main_window._actualizar_modelo_desde_ui() 
            else:
                log_message("Referencia a main_window o _actualizar_modelo_desde_ui no encontrada.", "warning")
                QMessageBox.warning(self, "Advertencia", "No se pudo sincronizar con los datos de entrada. La previsualización podría no estar actualizada.")
                # Continuar de todos modos con el modelo actual de esta pestaña
            
            # Actualizar los metadatos de esta propia pestaña por si acaso
            self.actualizar_modelo_meta()

            informe_generado = generar_informe_texto(self.modelo_informe)
            self.mostrar_informe_texto(informe_generado)
            log_message("Previsualización del informe generada/actualizada.", "debug")
        except Exception as e:
            log_message(f"Error al generar previsualización: {e}", "error", exc_info=True)
            QMessageBox.critical(self, "Error", f"No se pudo generar la previsualización: {e}")
            self.mostrar_informe_texto(f"Error al generar previsualización:\n{e}")

    @pyqtSlot()
    def on_copiar_informe_clicked(self):
        try:
            log_message("Botón 'Copiar Informe' pulsado.", "info")
            texto_a_copiar = self.texto_informe_display.toPlainText()
            if texto_a_copiar and texto_a_copiar != "Pulse 'Generar/Actualizar Previsualización' para ver el informe.":
                clipboard = QApplication.clipboard()
                clipboard.setText(texto_a_copiar)
                self.main_window.statusBar().showMessage("Informe copiado al portapapeles.", 3000)
                log_message("Informe copiado al portapapeles.", "debug")
            else:
                QMessageBox.information(self, "Información", "No hay contenido en la previsualización para copiar o aún no se ha generado.")
                log_message("Intento de copiar informe vacío o no generado.", "debug")
        except Exception as e:
            log_message(f"Error al copiar informe: {e}", "error", exc_info=True)
            QMessageBox.critical(self, "Error", f"No se pudo copiar el informe: {e}")

    def actualizar_modelo(self): # Redirigir a actualizar_modelo_meta para claridad
        self.actualizar_modelo_meta()