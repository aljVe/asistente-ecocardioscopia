# Creado por Alejandro Venegas Robles.
# En caso de incidencias, contactar con alejandro2196vr@gmail.com
# -*- coding: utf-8 -*-
"""
Pestaña para los datos del paciente.
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLineEdit, QDateEdit, QLabel
from PyQt5.QtCore import pyqtSignal, QDate # Import QDate
from datetime import datetime

from models import DatosPaciente # El sub-modelo específico para esta pestaña
from utils.error_handling import log_message

class PacienteTab(QWidget):
    # Señal emitida cuando los datos de esta pestaña cambian y deben reflejarse en el modelo
    datos_paciente_modificados = pyqtSignal(DatosPaciente)

    def __init__(self, modelo_paciente: DatosPaciente, parent=None):
        super().__init__(parent)
        self.modelo = modelo_paciente
        self._init_ui()
        self._conectar_senales()
        self.cargar_modelo_en_ui() # Cargar datos iniciales si el modelo ya tiene
        log_message("Pestaña PacienteTab inicializada.", "debug")

    def _init_ui(self):
        # --- INICIO: Marcador para localización de errores (UI PacienteTab) ---
        try:
            layout_principal = QVBoxLayout(self)
            
            grupo_datos = QGroupBox("Información del Paciente y Estudio")
            form_layout = QFormLayout()

            self.nhc_edit = QLineEdit()
            form_layout.addRow("NHC:", self.nhc_edit)

            self.nombre_edit = QLineEdit()
            form_layout.addRow("Nombre:", self.nombre_edit)
            
            self.apellidos_edit = QLineEdit()
            form_layout.addRow("Apellidos:", self.apellidos_edit)

            self.fecha_estudio_edit = QDateEdit()
            self.fecha_estudio_edit.setCalendarPopup(True)
            self.fecha_estudio_edit.setDate(QDate.currentDate()) # Fecha actual por defecto
            self.fecha_estudio_edit.setDisplayFormat("dd/MM/yyyy")
            form_layout.addRow("Fecha del Estudio:", self.fecha_estudio_edit)
            
            self.realizado_por_edit = QLineEdit() # Este campo podría estar en el modelo global del informe.
                                                # Si es así, esta pestaña debería acceder a self.modelo_informe.realizado_por
            # form_layout.addRow("Realizado por:", self.realizado_por_edit)


            grupo_datos.setLayout(form_layout)
            layout_principal.addWidget(grupo_datos)
            
            # Espacio para crecer si se añaden más campos
            layout_principal.addStretch(1)
            self.setLayout(layout_principal)
        except Exception as e:
            log_message(f"Error inicializando UI de PacienteTab: {e}", "error", exc_info=True)
        # --- FIN: Marcador para localización de errores (UI PacienteTab) ---

    def _conectar_senales(self):
        # Conectar señales de los QLineEdit, QDateEdit, etc. a un método que actualice el modelo
        # Usar textChanged o editingFinished según la necesidad
        self.nhc_edit.editingFinished.connect(self.actualizar_modelo)
        self.nombre_edit.editingFinished.connect(self.actualizar_modelo)
        self.apellidos_edit.editingFinished.connect(self.actualizar_modelo)
        self.fecha_estudio_edit.dateChanged.connect(self.actualizar_modelo)

    def set_modelo(self, nuevo_modelo_paciente: DatosPaciente):
        """Permite actualizar el modelo desde fuera (ej. al crear nuevo informe)."""
        # --- INICIO: Marcador para localización de errores (Set Modelo PacienteTab) ---
        try:
            log_message("Actualizando modelo en PacienteTab.", "debug")
            self.modelo = nuevo_modelo_paciente
            self.cargar_modelo_en_ui()
        except Exception as e:
            log_message(f"Error en set_modelo de PacienteTab: {e}", "error", exc_info=True)
        # --- FIN: Marcador para localización de errores (Set Modelo PacienteTab) ---

    def cargar_modelo_en_ui(self):
        """Carga los datos del modelo en los widgets de la UI."""
        # --- INICIO: Marcador para localización de errores (Cargar Modelo UI PacienteTab) ---
        try:
            self.nhc_edit.setText(self.modelo.nhc or "")
            self.nombre_edit.setText(self.modelo.nombre or "")
            self.apellidos_edit.setText(self.modelo.apellidos or "")
            
            # Para QDateEdit, convertir datetime a QDate
            if isinstance(self.modelo.fecha_estudio, datetime):
                qdate_estudio = QDate(self.modelo.fecha_estudio.year, 
                                      self.modelo.fecha_estudio.month, 
                                      self.modelo.fecha_estudio.day)
            else: # Si ya es QDate o None
                qdate_estudio = self.modelo.fecha_estudio if isinstance(self.modelo.fecha_estudio, QDate) else QDate.currentDate()
            self.fecha_estudio_edit.setDate(qdate_estudio)

        except Exception as e:
            log_message(f"Error cargando modelo en UI de PacienteTab: {e}", "error", exc_info=True)
        # --- FIN: Marcador para localización de errores (Cargar Modelo UI PacienteTab) ---

    def actualizar_modelo(self):
        """Actualiza el objeto self.modelo con los datos de la UI."""
        # --- INICIO: Marcador para localización de errores (Actualizar Modelo PacienteTab) ---
        try:
            self.modelo.nhc = self.nhc_edit.text().strip()
            self.modelo.nombre = self.nombre_edit.text().strip()
            self.modelo.apellidos = self.apellidos_edit.text().strip()
            
            # Convertir QDate a datetime.date o datetime
            qdate_obj = self.fecha_estudio_edit.date()
            self.modelo.fecha_estudio = datetime(qdate_obj.year(), qdate_obj.month(), qdate_obj.day())

            log_message(f"Modelo PacienteTab actualizado: NHC={self.modelo.nhc}", "debug")
            self.datos_paciente_modificados.emit(self.modelo) # Emitir señal si es necesario
        except Exception as e:
            log_message(f"Error actualizando modelo desde UI de PacienteTab: {e}", "error", exc_info=True)
        # --- FIN: Marcador para localización de errores (Actualizar Modelo PacienteTab) ---

# Las otras pestañas (EcoBasicaTab, EcoAvanzadaTab, CongestionTab, InformeTab) seguirían una estructura similar,
# manejando sus respectivos sub-modelos o partes del InformeEcoCompleto.
# Cada pestaña tendría sus propios widgets (QLineEdit, QComboBox, QCheckBox, QSpinBox)
# para capturar los datos del infograma.